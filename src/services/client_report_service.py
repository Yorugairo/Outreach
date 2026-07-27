"""Offline, deterministic client report bundle renderer."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path, PurePosixPath
from string import Template
from typing import Any

from src.models import AgenticFinding, ClientReportBundle, ReportSnapshot, canonical_sha256
from src.services.provenance_service import EvidenceReferenceError, validate_evidence_ref
from src.services.report_manifest_service import ReportManifestService


class ClientReportService:
    """Render a client bundle from one immutable snapshot and optional assessment."""

    RENDERER_VERSION = "client-renderer.v1"
    THEME_VERSION = "client.default.v1"

    def __init__(
        self,
        repository: Any | None = None,
        artifact_root: str | Path = "artifacts/seo_insight_runs",
        output_root: str | Path | None = None,
        *,
        renderer_version: str = RENDERER_VERSION,
        theme_version: str = THEME_VERSION,
    ) -> None:
        self.repository = repository
        self.artifact_root = Path(artifact_root)
        self.output_root = Path(output_root) if output_root is not None else self.artifact_root
        self.renderer_version = renderer_version
        self.theme_version = theme_version
        template_path = Path(__file__).resolve().parents[1] / "templates" / "client_report_v1.html"
        theme_path = Path(__file__).resolve().parents[1] / "templates" / "client_theme_v1.json"
        self.template = Template(template_path.read_text(encoding="utf-8"))
        self.theme = json.loads(theme_path.read_text(encoding="utf-8"))

    def render(
        self,
        snapshot: ReportSnapshot | str,
        *,
        assessment: Any | None = None,
        payload: dict[str, Any] | None = None,
        bundle_id: str | None = None,
    ) -> ClientReportBundle:
        snapshot = self._resolve_snapshot(snapshot)
        payload = payload if payload is not None else self._load_payload(snapshot)
        if canonical_sha256(payload) != snapshot.payload_sha256:
            raise ValueError("report snapshot payload hash does not match immutable payload")
        safe_findings, assessment_state = self._safe_findings(assessment)
        safe_findings = self._resolve_safe_findings(snapshot, safe_findings)
        assessment_state["customer_safe_findings"] = len(safe_findings)
        bundle_id = bundle_id or self._bundle_id(snapshot, safe_findings, assessment_state)
        bundle_dir = self.output_root / "bundles" / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "data").mkdir(exist_ok=True)
        (bundle_dir / "assets").mkdir(exist_ok=True)

        assets = self._copy_assets(bundle_dir, payload)
        assets.extend(self._copy_evidence_assets(bundle_dir, snapshot, safe_findings))
        assets = list({item["path"]: item for item in assets}.values())
        claims = self._claims(payload, safe_findings, snapshot)
        report_data = self._report_data(snapshot, payload, safe_findings, assessment_state, claims, assets)
        report_bytes = json.dumps(report_data, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"
        (bundle_dir / "data" / "report.json").write_bytes(report_bytes)

        sections = self._sections(report_data)
        target = self._target(payload, snapshot)
        html_bytes = self.template.substitute(
            title=f"SEO insight report — {target}",
            target=html.escape(target),
            headline=html.escape(sections["headline"]),
            summary=html.escape(sections["summary"]),
            css=self.theme.get("css", ""),
            brief=sections["brief"],
            evidence=sections["evidence"],
            methodology=sections["methodology"],
            snapshot_id=html.escape(snapshot.id),
            renderer_version=html.escape(self.renderer_version),
        ).encode("utf-8")
        (bundle_dir / "report.html").write_bytes(html_bytes)
        pdf_bytes = self._fallback_pdf(sections["headline"], sections["summary"], snapshot.id)
        (bundle_dir / "report.pdf").write_bytes(pdf_bytes)

        manifest_service = ReportManifestService()
        file_entries = [
            manifest_service.file_entry(bundle_dir, "report.html", role="html"),
            manifest_service.file_entry(bundle_dir, "report.pdf", role="pdf"),
            manifest_service.file_entry(bundle_dir, "data/report.json", role="json"),
        ]
        manifest = manifest_service.build_manifest(
            bundle_id=bundle_id,
            snapshot=snapshot,
            files=file_entries,
            theme_version=self.theme_version,
            renderer_version=self.renderer_version,
            claims=claims,
            assets=assets,
            assessment=assessment_state,
        )
        _, manifest_hash = manifest_service.write_manifest(bundle_dir, manifest)
        all_hash_entries = file_entries + [
            manifest_service.file_entry(bundle_dir, str(item["path"]), role="asset") for item in assets
        ]
        # The manifest cannot list its own hash without a recursive fixed point,
        # but the portable checksum file can still cover it.
        manifest_entry = manifest_service.file_entry(bundle_dir, "manifest.json", role="manifest")
        manifest_service.write_hashes(bundle_dir, all_hash_entries + [manifest_entry])
        files = all_hash_entries + [manifest_entry, manifest_service.file_entry(bundle_dir, "hashes.sha256", role="hashes")]
        # The manifest intentionally does not list itself: hashing it recursively would be undefined.
        bundle = ClientReportBundle(
            id=bundle_id,
            report_snapshot_id=snapshot.id,
            run_id=snapshot.run_id,
            manifest_sha256=manifest_hash,
            manifest_artifact_ref=f"bundles/{bundle_id}/manifest.json",
            files=files,
            theme_version=self.theme_version,
            renderer_version=self.renderer_version,
            status="complete",
            created_at=snapshot.created_at,
        )
        if self.repository is not None:
            bundle = self.repository.save_client_report_bundle(bundle)
        return bundle

    generate = render
    build_bundle = render

    def validate(self, bundle: ClientReportBundle | str) -> dict[str, Any]:
        resolved = bundle
        if not isinstance(resolved, ClientReportBundle) and self.repository is not None:
            resolved = self.repository.get_client_report_bundle(str(bundle))
        bundle_id = resolved.id if isinstance(resolved, ClientReportBundle) else str(bundle)
        root = self.output_root / "bundles" / bundle_id
        manifest_path = root / "manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        if (
            isinstance(resolved, ClientReportBundle)
            and ReportManifestService.sha256_bytes(manifest_bytes) != resolved.manifest_sha256
        ):
            raise ValueError("client bundle manifest hash does not match its immutable record")
        manifest = json.loads(manifest_bytes)
        return ReportManifestService.validate_manifest(root, manifest)

    def _resolve_snapshot(self, snapshot: ReportSnapshot | str) -> ReportSnapshot:
        if isinstance(snapshot, ReportSnapshot):
            return snapshot
        if self.repository is None:
            raise ValueError("a repository is required when rendering by snapshot ID")
        resolved = self.repository.get_report_snapshot(snapshot)
        if resolved is None:
            raise ValueError(f"report snapshot {snapshot} does not exist")
        return resolved

    def _load_payload(self, snapshot: ReportSnapshot) -> dict[str, Any]:
        ref = str(snapshot.payload_artifact_ref)
        candidate = self._artifact_path(ref)
        if not candidate.is_file():
            raise FileNotFoundError(f"report snapshot payload is missing: {ref}")
        value = json.loads(candidate.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("report snapshot payload must be a JSON object")
        return value

    def _bundle_id(
        self,
        snapshot: ReportSnapshot,
        findings: list[dict[str, Any]],
        assessment_state: dict[str, Any],
    ) -> str:
        rendering_hash = canonical_sha256(
            {
                "snapshot_id": snapshot.id,
                "payload_sha256": snapshot.payload_sha256,
                "renderer_version": self.renderer_version,
                "theme_version": self.theme_version,
                "assessment": assessment_state,
                "findings": findings,
            }
        )
        return f"{snapshot.id}-{rendering_hash[:16]}"

    @staticmethod
    def _safe_findings(assessment: Any | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if assessment is None:
            return [], {"status": "unknown", "customer_safe_findings": 0, "disclosure": "No validated customer-safe agentic assessment was available."}
        payload = assessment.to_dict() if hasattr(assessment, "to_dict") else dict(assessment)
        raw = payload.get("findings", []) if isinstance(payload.get("findings", []), list) else []
        findings: list[dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict) or item.get("customer_safe") is not True or not item.get("evidence_refs"):
                continue
            try:
                AgenticFinding(**item)
            except (TypeError, ValueError):
                continue
            findings.append(dict(item))
        validation = payload.get("validation_result") if isinstance(payload.get("validation_result"), dict) else {}
        state = "validated" if validation.get("customer_safe") is True else "needs_review"
        return findings, {
            "status": state,
            "assessment_id": payload.get("id"),
            "runtime": payload.get("runtime"),
            "requested_model": payload.get("requested_model"),
            "served_provider": payload.get("served_provider"),
            "served_model": payload.get("served_model"),
            "prompt_version": payload.get("prompt_version"),
            "rubric_version": payload.get("rubric_version"),
            "customer_safe_findings": len(findings),
            "disclosure": "Only findings marked customer_safe with independently resolved evidence are included.",
        }

    def _resolve_safe_findings(
        self,
        snapshot: ReportSnapshot,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        run_dir = self.artifact_root / "runs" / snapshot.run_id
        resolved: list[dict[str, Any]] = []
        for finding in findings:
            try:
                for ref in finding["evidence_refs"]:
                    validate_evidence_ref(
                        run_dir,
                        ref,
                        expected_attempt_id=snapshot.attempt_id,
                    )
            except (EvidenceReferenceError, KeyError, TypeError):
                continue
            resolved.append(finding)
        return resolved

    @staticmethod
    def _target(payload: dict[str, Any], snapshot: ReportSnapshot) -> str:
        for key in ("normalized_domain", "domain", "target", "requested_domain"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for container in (payload.get("target"), payload.get("target_facts"), payload.get("run")):
            if isinstance(container, dict):
                for key in ("normalized_domain", "domain", "requested_domain", "display_name"):
                    if container.get(key):
                        return str(container[key])
        return snapshot.run_id

    def _report_data(self, snapshot: ReportSnapshot, payload: dict[str, Any], findings: list[dict[str, Any]], state: dict[str, Any], claims: list[dict[str, Any]], assets: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "contract_version": "client-report.v1",
            "snapshot": {
                "id": snapshot.id,
                "run_id": snapshot.run_id,
                "attempt_id": snapshot.attempt_id,
                "report_contract": snapshot.report_contract,
                "schema_version": snapshot.schema_version,
                "payload_sha256": snapshot.payload_sha256,
                "payload_artifact_ref": snapshot.payload_artifact_ref,
                "source_snapshot_ids": dict(sorted(snapshot.source_snapshot_ids.items())),
                "source_hashes": dict(sorted(snapshot.source_hashes.items())),
                "completeness_percent": snapshot.completeness_percent,
                "status": snapshot.status,
            },
            "layers": {
                "brief": self._brief(payload, claims),
                "evidence": {"source_refs": dict(sorted(snapshot.source_snapshot_ids.items())), "source_hashes": dict(sorted(snapshot.source_hashes.items())), "claims": claims, "assets": assets},
                "methodology": {"renderer_version": self.renderer_version, "theme_version": self.theme_version, "assessment": state, "limitations": ["Scores and observations are sourced from the immutable snapshot.", "Unknown or review-required evidence is not presented as fact."]},
            },
            "assessment": state,
        }

    @staticmethod
    def _brief(payload: dict[str, Any], claims: list[dict[str, Any]]) -> dict[str, Any]:
        scores: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, dict) and ("score" in value or key.endswith("surface")):
                if "score" in value:
                    scores[key] = value.get("score")
        return {"headline": payload.get("headline") or payload.get("title") or "SEO insight report", "summary": payload.get("executive_summary") or payload.get("summary") or "Evidence-backed findings from this snapshot.", "scores": scores, "claim_ids": [item["id"] for item in claims]}

    @staticmethod
    def _claims(payload: dict[str, Any], findings: list[dict[str, Any]], snapshot: ReportSnapshot) -> list[dict[str, Any]]:
        claims: list[dict[str, Any]] = [
            {
                "id": "report:headline",
                "kind": "deterministic_text",
                "text": str(payload.get("headline") or payload.get("title") or "SEO insight report"),
                "source_snapshot_id": snapshot.id,
                "source_hash": snapshot.payload_sha256,
            },
            {
                "id": "report:summary",
                "kind": "deterministic_text",
                "text": str(payload.get("executive_summary") or payload.get("summary") or "Evidence-backed findings from this snapshot."),
                "source_snapshot_id": snapshot.id,
                "source_hash": snapshot.payload_sha256,
            },
        ]
        for key, value in sorted(payload.items()):
            if isinstance(value, dict) and "score" in value:
                claims.append({"id": f"surface:{key}:score", "kind": "deterministic_metric", "text": f"{key} score: {value.get('score')}", "value": value.get("score"), "source_snapshot_id": snapshot.id, "source_hash": snapshot.payload_sha256})
        for finding in sorted(findings, key=lambda item: str(item.get("id", ""))):
            claims.append({"id": f"finding:{finding.get('id')}", "kind": "validated_assessment", "text": finding.get("claim", ""), "source_snapshot_id": snapshot.id, "source_hash": snapshot.payload_sha256, "evidence_refs": finding.get("evidence_refs", [])})
        return claims

    def _sections(self, data: dict[str, Any]) -> dict[str, str]:
        brief = data["layers"]["brief"]
        scores = brief.get("scores", {})
        score_html = "".join(f'<div class="card" data-claim="surface:{html.escape(str(key))}:score"><strong>{html.escape(str(key))}</strong>: {html.escape(str(value))}</div>' for key, value in sorted(scores.items())) or '<p class="unknown">No scored surface was available.</p>'
        evidence = data["layers"]["evidence"]
        claim_html = "".join(f'<div class="card" data-claim="{html.escape(str(item["id"]))}">{html.escape(str(item.get("text", "")))}</div>' for item in evidence.get("claims", [])) or '<p class="unknown">No validated customer-safe assessment findings were available.</p>'
        methodology = data["layers"]["methodology"]
        model = methodology["assessment"]
        return {"headline": str(brief.get("headline", "SEO insight report")), "summary": str(brief.get("summary", "Evidence-backed findings from this snapshot.")), "brief": score_html, "evidence": claim_html, "methodology": f'<p>Renderer <code>{html.escape(self.renderer_version)}</code>; theme <code>{html.escape(self.theme_version)}</code>.</p><p>Agentic analysis status: <strong>{html.escape(str(model.get("status", "unknown")))}</strong>. Only validated customer-safe findings with resolved evidence are shown.</p>'}

    @staticmethod
    def _fallback_pdf(headline: str, summary: str, snapshot_id: str) -> bytes:
        text = re.sub(r"[^\x20-\x7e]", "", f"{headline}\n{summary}\nSnapshot {snapshot_id}")[:1800]
        chunks = []
        for line in text.splitlines():
            escaped = line.replace("(", "\\(").replace(")", "\\)")
            chunks.append(f"({escaped}) Tj 0 -18 Td")
        stream = "BT /F1 12 Tf 50 760 Td " + " ".join(chunks) + " ET"
        objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream".encode("latin-1")]
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(objects, 1):
            offsets.append(len(out)); out.extend(f"{index} 0 obj\n".encode()); out.extend(obj); out.extend(b"\nendobj\n")
        xref = len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode()); out.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])); out.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()); return bytes(out)

    def _copy_assets(self, bundle_dir: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
        assets: list[dict[str, Any]] = []
        seen: set[str] = set()
        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key in {"artifact_path", "asset_path", "source_path", "file_path", "screenshot_path"} and isinstance(item, str):
                        self._copy_asset(bundle_dir, item, value, assets, seen)
                    else:
                        walk(item)
            elif isinstance(value, list):
                for item in value: walk(item)
        walk(payload)
        return assets

    def _copy_asset(self, bundle_dir: Path, ref: str, metadata: dict[str, Any], assets: list[dict[str, Any]], seen: set[str]) -> None:
        if ref in seen: return
        seen.add(ref)
        try:
            source = self._artifact_path(ref)
        except ValueError:
            return
        if not source.is_file(): return
        data = source.read_bytes(); digest = ReportManifestService.sha256_bytes(data)
        expected = metadata.get("sha256")
        if expected and expected != digest: return
        ext = source.suffix.lower() if source.suffix and len(source.suffix) <= 8 else ".bin"
        relative = f"assets/{digest}{ext}"
        dest = bundle_dir / Path(*PurePosixPath(relative).parts); dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists(): dest.write_bytes(data)
        source_ref = source.relative_to(self.artifact_root.resolve()).as_posix()
        assets.append({"path": relative, "sha256": digest, "bytes": len(data), "mime_type": metadata.get("content_type") or "application/octet-stream", "source_ref": source_ref})

    def _copy_evidence_assets(
        self,
        bundle_dir: Path,
        snapshot: ReportSnapshot,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        assets: list[dict[str, Any]] = []
        run_dir = (self.artifact_root / "runs" / snapshot.run_id).resolve()
        for finding in findings:
            for ref in finding["evidence_refs"]:
                source = (run_dir / Path(*PurePosixPath(ref["artifact_path"]).parts)).resolve()
                source.relative_to(run_dir)
                data = source.read_bytes()
                digest = ReportManifestService.sha256_bytes(data)
                relative = f"assets/{digest}.json"
                destination = bundle_dir / Path(*PurePosixPath(relative).parts)
                if not destination.exists():
                    destination.write_bytes(data)
                assets.append(
                    {
                        "path": relative,
                        "sha256": digest,
                        "bytes": len(data),
                        "mime_type": "application/json",
                        "evidence_ref": ref["artifact_path"],
                    }
                )
        return assets

    def _artifact_path(self, ref: str) -> Path:
        root = self.artifact_root.resolve()
        raw = Path(ref)
        candidate = raw.resolve() if raw.is_absolute() else (
            root / Path(*PurePosixPath(ref).parts)
        ).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("artifact path escapes the configured artifact root") from exc
        return candidate
