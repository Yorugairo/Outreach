"""Content-addressed backup store for canonical assets (Cloudflare R2).

The catalogue already records a sha256 for every asset it names; this module
makes that digest the storage key — ``sha256/<digest>`` in an S3-compatible
bucket. Backup becomes a checkable invariant (every digest the catalogue names
exists in the store) instead of a chore, and restore is the same walk in
reverse.

Sync happens **on promote**: the moment an asset becomes canonical is the
moment it becomes irreplaceable, so that is the moment it uploads. There is no
scheduled sync and no drift window.

Two backends behind one protocol:

- **Local directory** (``VIDEO_ENGINE_STORE_DIR``): a content-addressed folder,
  ideally on a different physical drive. No credentials, no network. The
  operator's choice while the pipeline is still settling (2026-08-24).
- **Cloudflare R2** (the ``VIDEO_ENGINE_R2_*`` variables below): same layout
  over S3. Switching later is an environment change, never a code change.

    VIDEO_ENGINE_STORE_DIR              local content-addressed store root
    VIDEO_ENGINE_R2_ENDPOINT            https://<account>.r2.cloudflarestorage.com
    VIDEO_ENGINE_R2_BUCKET              bucket name
    VIDEO_ENGINE_R2_ACCESS_KEY_ID
    VIDEO_ENGINE_R2_SECRET_ACCESS_KEY

When both are set, the local directory wins — explicit local intent beats
stale cloud credentials.

With no configuration, promotion fails closed. The explicit opt-out
``VIDEO_ENGINE_ALLOW_UNSYNCED_PROMOTE=1`` lets a promote proceed offline; the
entries are then marked ``"unsynced": true`` so the audit can surface them —
silence is never the failure mode.

The S3 client sits behind one adapter (``_build_client``) so tests fake the
protocol and never touch the network.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

ENV_STORE_DIR = "VIDEO_ENGINE_STORE_DIR"
ENV_ENDPOINT = "VIDEO_ENGINE_R2_ENDPOINT"
ENV_BUCKET = "VIDEO_ENGINE_R2_BUCKET"
ENV_KEY_ID = "VIDEO_ENGINE_R2_ACCESS_KEY_ID"
ENV_SECRET = "VIDEO_ENGINE_R2_SECRET_ACCESS_KEY"
ENV_ALLOW_UNSYNCED = "VIDEO_ENGINE_ALLOW_UNSYNCED_PROMOTE"

KEY_PREFIX = "sha256"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class AssetStoreError(Exception):
    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


class StoreClient(Protocol):
    """The minimal protocol the store needs; tests fake it in a dict."""

    def head(self, key: str) -> bool: ...
    def put(self, key: str, path: Path) -> None: ...
    def get(self, key: str, path: Path) -> None: ...


def key_for(digest: str) -> str:
    if not _DIGEST.match(str(digest or "")):
        raise AssetStoreError([f"{digest!r} is not a lowercase hex sha256 digest"])
    return f"{KEY_PREFIX}/{digest}"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class AssetStore:
    def __init__(self, client: StoreClient, bucket: str):
        self._client = client
        self.bucket = bucket

    def has(self, digest: str) -> bool:
        return self._client.head(key_for(digest))

    def ensure(self, digest: str, path: str | Path) -> str:
        """Upload the file under its digest; idempotent. Returns what happened.

        The local bytes are verified against the digest before any upload — a
        store holding wrong bytes under a digest key would poison restore.
        """

        source = Path(path)
        if not source.exists():
            raise AssetStoreError([f"no file at {source}"])
        actual = _file_sha256(source)
        if actual != digest:
            raise AssetStoreError([
                f"{source} hashes to {actual}, not the catalogue digest {digest}"
            ])
        key = key_for(digest)
        if self._client.head(key):
            return "exists"
        self._client.put(key, source)
        return "uploaded"

    def fetch(self, digest: str, destination: str | Path) -> Path:
        """Download by digest and verify the bytes before letting them stand."""

        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        self._client.get(key_for(digest), target)
        actual = _file_sha256(target)
        if actual != digest:
            target.unlink(missing_ok=True)
            raise AssetStoreError([
                f"store returned bytes hashing to {actual} for {digest}; refusing them"
            ])
        return target


class LocalDirClient:
    """Content-addressed store in a plain directory; same keys as the bucket."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        return self.root / key

    def head(self, key: str) -> bool:
        return self._path(key).exists()

    def put(self, key: str, path: Path) -> None:
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        import shutil as _shutil

        _shutil.copy2(path, target)

    def get(self, key: str, path: Path) -> None:
        import shutil as _shutil

        _shutil.copy2(self._path(key), path)


def _build_client(env: Mapping[str, str]) -> StoreClient:
    """The single network boundary. Imports boto3 lazily; names its absence."""

    try:
        import boto3  # noqa: PLC0415 — optional dependency, imported at the edge
    except ImportError:
        raise AssetStoreError([
            "boto3 is not installed; the asset store needs it "
            "(python -m pip install boto3)"
        ])
    s3 = boto3.client(
        "s3",
        endpoint_url=env[ENV_ENDPOINT],
        aws_access_key_id=env[ENV_KEY_ID],
        aws_secret_access_key=env[ENV_SECRET],
        region_name="auto",
    )
    bucket = env[ENV_BUCKET]

    class _Boto:
        def head(self, key: str) -> bool:
            try:
                s3.head_object(Bucket=bucket, Key=key)
                return True
            except s3.exceptions.ClientError as error:
                if error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
                    return False
                raise

        def put(self, key: str, path: Path) -> None:
            s3.upload_file(str(path), bucket, key)

        def get(self, key: str, path: Path) -> None:
            s3.download_file(bucket, key, str(path))

    return _Boto()


def from_env(env: Mapping[str, str] | None = None) -> AssetStore | None:
    """The configured store, or ``None`` when no configuration is present."""

    source = os.environ if env is None else env
    local = source.get(ENV_STORE_DIR)
    if local:
        root = Path(local).expanduser()
        root.mkdir(parents=True, exist_ok=True)
        return AssetStore(LocalDirClient(root), f"dir:{root}")
    names = (ENV_ENDPOINT, ENV_BUCKET, ENV_KEY_ID, ENV_SECRET)
    present = [name for name in names if source.get(name)]
    if not present:
        return None
    missing = [name for name in names if not source.get(name)]
    if missing:
        raise AssetStoreError([
            f"asset store partially configured; missing {', '.join(missing)}"
        ])
    return AssetStore(_build_client(source), source[ENV_BUCKET])


def _entry_files(entry: Mapping[str, Any], project_root: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    if entry.get("sha256") and entry.get("path"):
        files.append((str(entry["sha256"]), project_root / str(entry["path"])))
    for layer in entry.get("layers") or []:
        if layer.get("sha256") and layer.get("path"):
            files.append((str(layer["sha256"]), project_root / str(layer["path"])))
    return files


def sync_promoted_entries(
    entries: Sequence[Mapping[str, Any]],
    project_root: str | Path,
    *,
    env: Mapping[str, str] | None = None,
    store: AssetStore | None = None,
) -> list[dict[str, Any]]:
    """Upload every promoted file by digest, before the catalogue write.

    Returns the entries to register. On sync failure the promotion fails —
    a canonical asset must never exist unprotected in silence. With no store
    configured, the explicit opt-out lets the promote proceed with every entry
    marked ``"unsynced": true`` for the audit to surface.
    """

    source = os.environ if env is None else env
    resolved = store if store is not None else from_env(source)
    root = Path(project_root)

    if resolved is None:
        if source.get(ENV_ALLOW_UNSYNCED) == "1":
            return [{**dict(entry), "unsynced": True} for entry in entries]
        raise AssetStoreError([
            "no asset store configured, so promotion would leave canonical "
            f"assets unprotected. Set {ENV_ENDPOINT}, {ENV_BUCKET}, "
            f"{ENV_KEY_ID} and {ENV_SECRET} — or set {ENV_ALLOW_UNSYNCED}=1 "
            "to promote unsynced deliberately.",
        ])

    errors: list[str] = []
    for entry in entries:
        for digest, path in _entry_files(entry, root):
            try:
                resolved.ensure(digest, path)
            except AssetStoreError as exc:
                errors.extend(f"{entry.get('asset_id')}: {e}" for e in exc.errors)
    if errors:
        raise AssetStoreError(errors)
    return [dict(entry) for entry in entries]


def _catalog_digest_paths(catalog: Mapping[str, Any]) -> list[tuple[str, str, str, bool]]:
    """(asset_id, digest, path, unsynced) for every file the catalogue names."""

    rows: list[tuple[str, str, str, bool]] = []
    for asset in catalog.get("assets", []):
        unsynced = bool(asset.get("unsynced"))
        if asset.get("sha256") and asset.get("path"):
            rows.append((str(asset["asset_id"]), str(asset["sha256"]), str(asset["path"]), unsynced))
        for layer in asset.get("layers") or []:
            if layer.get("sha256") and layer.get("path"):
                rows.append((str(asset["asset_id"]), str(layer["sha256"]), str(layer["path"]), unsynced))
    return rows


def audit_catalog(catalog: Mapping[str, Any], store: AssetStore) -> dict[str, Any]:
    """Every digest the catalogue names, checked against the store. Read-only.

    ``unsynced`` entries (promoted under the explicit opt-out) are reported
    separately — they are the debt the opt-out created.
    """

    ok, missing, unsynced = [], [], []
    for asset_id, digest, path, was_unsynced in _catalog_digest_paths(catalog):
        record = {"asset_id": asset_id, "sha256": digest, "path": path}
        if was_unsynced:
            unsynced.append(record)
        if store.has(digest):
            ok.append(record)
        elif not was_unsynced:
            missing.append(record)
    return {
        "ok": len(ok),
        "missing": missing,
        "unsynced": unsynced,
        "total": len(ok) + len(missing) + len([u for u in unsynced if u not in ok]),
    }


def restore_catalog(
    catalog: Mapping[str, Any],
    project_root: str | Path,
    store: AssetStore,
    *,
    digests: Sequence[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Rebuild catalogue-named files from the store, verifying every byte.

    A bare catalogue plus credentials is the whole disaster-recovery contract.
    Existing files are refused without ``force`` so a live tree is never
    silently overwritten.
    """

    root = Path(project_root)
    wanted = set(digests) if digests else None
    restored, skipped, errors = [], [], []
    for asset_id, digest, path, _ in _catalog_digest_paths(catalog):
        if wanted is not None and digest not in wanted:
            continue
        destination = root / path
        if destination.exists() and not force:
            skipped.append({"asset_id": asset_id, "path": path, "reason": "exists; use force"})
            continue
        try:
            store.fetch(digest, destination)
            restored.append({"asset_id": asset_id, "path": path})
        except AssetStoreError as exc:
            errors.extend(f"{asset_id}: {e}" for e in exc.errors)
    if errors:
        raise AssetStoreError(errors)
    return {"restored": restored, "skipped": skipped}
