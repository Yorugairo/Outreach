"""GATES REGISTRY - every speech-writing gate, generated FROM the tools that enforce it.

Operator, 2026-09-05: "we need all of the speech-writing gates easily searched,
referenced, and understood." The gates live as `add("G04", "<rule>", <level>, <msg>)`
calls inside the checkers and the docs cite them by id; nothing listed them in one
place that could not drift. This builds that list from the SOURCE of the tools, so
the id, the rule text, the doc citation and the tests are always what the code says.

    python content/video_engine/scripts/build_gates_registry.py [--write | --check]

`--write` regenerates `docs/GATES-REGISTRY.jsonl` + `.md`; `--check` (the default)
exits 1 with a one-line diff summary when either artifact is stale.

HOW IT READS THE TOOLS (`ast` only - the tools are never imported or executed):

  1. Every module-level dataclass whose fields carry the roles id / level / rule /
     message is a ROW TYPE (`Gate`, `Row`, `Finding`). Field ORDER gives the role of
     each positional argument, so a tool that reorders its dataclass reorders here too.
  2. `add = lambda i, src, lvl, m: g.append(Gate(i, src, lvl, m))` and
     `def add(level, rule, msg): out.append(Finding(level, rule, msg))` are EMITTERS:
     each parameter's role is read through the constructor call in the body, never
     guessed from its name.
  3. Every call to a row type or an emitter becomes a record. A rule argument that is
     a plain string literal is taken verbatim; a NAME (`SRC_G45`, `src9`) resolves to
     the nearest preceding assignment; an f-string is rendered from its source with
     each placeholder as `{expr}`, and `{NAME=value}` when NAME is a literal constant
     of the module - so a threshold is greppable by name AND by value.
  4. Levels come from the level argument: a literal, both arms of `"FAIL" if x else
     "PASS"`, a constant name, else every level token in the expression's source.
     `lint_script_pattern.py` has no level argument, so the level comes from the list
     its finding lands in (`failures` -> FAIL, `warnings` -> WARN) in `lint_script`.
  5. IDs: the row's own id when it has one (`G15b`, `M16`, `V01`); otherwise a stable
     slug of the rule text or finding code (`audit:doc-37-sec-1`, `lint:passive-ratio`).
  6. Doc citations inside the rule text (`38 B2`, `51.2`, `s9.29`, `MAP s3`, `P1 QC`,
     `E24`) resolve against `docs/DOCS-INDEX.jsonl` to a path:line; unresolved cites
     keep a null path rather than disappearing.
  7. Tests: every file under `content/video_engine/tests/` whose text mentions the id.

A gate whose rule text differs between branches (G31 states three different rules)
gets one record per distinct rule text, all under the same id - the code is the truth.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import io
import json
import re
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPTS_REL = "content/video_engine/scripts"
TESTS_REL = "content/video_engine/tests"
DOCS_INDEX_REL = "docs/DOCS-INDEX.jsonl"
JSONL_REL = "docs/GATES-REGISTRY.jsonl"
MD_REL = "docs/GATES-REGISTRY.md"
BUILD_CMD = "python content/video_engine/scripts/build_gates_registry.py --write"

# The checkers, and the family each one's rows belong to. The runner has no rows of
# its own - it composes, and the Composition block is generated from it.
FAMILY = {
    "gate_opening_structure.py": "opening",      # split per function, see OPENING_FAMILY
    "gate_motion_density.py": "motion",
    "audit_script_doctrine.py": "audit",
    "lint_script_pattern.py": "lint",
    "viewer_score.py": "viewer",
}
OPENING_FAMILY = {"run": "opening-long", "run_short": "opening-short"}
OPENING_SHARED = "opening-shared"
RUNNER = "run_script_gates.py"
FAMILIES = ("opening-long", "opening-short", "opening-shared", "motion", "audit",
            "lint", "viewer", "runner")

LEVELS = ("FAIL", "WARN", "PASS", "JUDGE", "INFO")
LEVEL_RE = re.compile(r"\b(" + "|".join(LEVELS) + r")\b")
ROLE_FIELDS = {"id": "id", "code": "code", "level": "level", "src": "rule",
               "rule": "rule", "message": "message", "msg": "message"}
SLUG_MAX = 60


# ---- the source model -------------------------------------------------------

@dataclass(frozen=True)
class Emitter:
    """A helper that constructs a row: which role each positional argument carries."""
    name: str
    line: int
    roles: tuple[str | None, ...]


@dataclass(frozen=True)
class Module:
    rel: str
    tree: ast.Module
    src: str


def _parse(path: Path, rel: str) -> Module:
    src = path.read_text(encoding="utf-8")
    return Module(rel, ast.parse(src), src)


def row_types(tree: ast.Module) -> dict[str, tuple[str | None, ...]]:
    """{class name: role per field, in declaration order} for every row dataclass."""
    out: dict[str, tuple[str | None, ...]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        roles = tuple(ROLE_FIELDS.get(st.target.id)
                      for st in node.body
                      if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name))
        if any(r in ("id", "code", "rule", "message") for r in roles):
            out[node.name] = roles
    return out


def _calls(node: ast.AST) -> list[ast.Call]:
    return [n for n in ast.walk(node) if isinstance(n, ast.Call)]


def _roles_through(body: ast.AST, params: list[str],
                   types: dict[str, tuple[str | None, ...]]) -> tuple[str | None, ...] | None:
    """Map an emitter's parameters onto row roles through the constructor it calls."""
    for call in _calls(body):
        if not (isinstance(call.func, ast.Name) and call.func.id in types):
            continue
        fields = types[call.func.id]
        roles: list[str | None] = [None] * len(params)
        for pos, arg in enumerate(call.args):
            if isinstance(arg, ast.Name) and arg.id in params and pos < len(fields):
                roles[params.index(arg.id)] = fields[pos]
        if any(roles):
            return tuple(roles)
    return None


def emitters(tree: ast.Module, types: dict[str, tuple[str | None, ...]]) -> list[Emitter]:
    """`add = lambda ...` and `def add(...)` helpers, with their argument roles."""
    out: list[Emitter] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Lambda) \
                and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            params = [a.arg for a in node.value.args.args]
            roles = _roles_through(node.value.body, params, types)
            if roles:
                out.append(Emitter(node.targets[0].id, node.lineno, roles))
        elif isinstance(node, ast.FunctionDef):
            params = [a.arg for a in node.args.args]
            roles = _roles_through(node, params, types)
            if roles:
                out.append(Emitter(node.name, node.lineno, roles))
    return sorted(out, key=lambda e: (e.name, e.line))


def bindings(tree: ast.Module) -> list[tuple[str, int, ast.AST]]:
    """Every `NAME = <expression>` assignment, with its line - what a rule or a level
    argument given as a bare name (`SRC_G45`, `src9`, `lvl`) resolves through."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            out.append((node.targets[0].id, node.lineno, node.value))
    return sorted(out, key=lambda c: c[1])


def _lookup(consts: list[tuple[str, int, ast.AST]], name: str, line: int) -> ast.AST | None:
    """The nearest assignment to `name` above `line`, else the first one anywhere."""
    hits = [c for c in consts if c[0] == name]
    before = [c for c in hits if c[1] <= line]
    chosen = before[-1] if before else (hits[0] if hits else None)
    return chosen[2] if chosen else None


def top_functions(tree: ast.Module) -> list[tuple[int, int, str]]:
    """(first line, last line, name) for every top-level function."""
    return [(n.lineno, n.end_lineno or n.lineno, n.name)
            for n in tree.body if isinstance(n, ast.FunctionDef)]


def enclosing(funcs: list[tuple[int, int, str]], line: int) -> str:
    return next((name for lo, hi, name in funcs if lo <= line <= hi), "")


# ---- rule text and levels ---------------------------------------------------

def _literal(consts: list[tuple[str, int, ast.AST]], name: str, line: int) -> str | None:
    node = _lookup(consts, name, line)
    if isinstance(node, ast.Constant) and not isinstance(node.value, str):
        return repr(node.value) if not isinstance(node.value, bool) else str(node.value)
    return None


def rule_text(node: ast.AST | None, mod: Module,
              consts: list[tuple[str, int, ast.AST]], line: int, depth: int = 0) -> str | None:
    """A rule argument as text: literal verbatim, name resolved, f-string rendered."""
    if node is None or depth > 3:
        return None
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.Name):
        return rule_text(_lookup(consts, node.id, line), mod, consts, line, depth + 1)
    if isinstance(node, ast.JoinedStr):
        return _render_fstring(node, mod, consts, line)
    return None


def _render_fstring(node: ast.JoinedStr, mod: Module,
                    consts: list[tuple[str, int, ast.AST]], line: int) -> str:
    parts: list[str] = []
    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            parts.append(value.value)
            continue
        if not isinstance(value, ast.FormattedValue):
            continue
        seg = " ".join((ast.get_source_segment(mod.src, value.value) or "?").split())
        if isinstance(value.value, ast.Name):
            lit = _literal(consts, value.value.id, line)
            if lit is not None:
                seg = f"{seg}={lit}"
        parts.append("{" + seg + "}")
    return "".join(parts)


def levels_of(node: ast.AST | None, mod: Module,
              consts: list[tuple[str, int, ast.AST]], line: int, depth: int = 0) -> list[str]:
    """Every level the call can emit, from the level expression."""
    if node is None or depth > 3:
        return []
    if isinstance(node, ast.Constant):
        return [node.value] if isinstance(node.value, str) and node.value in LEVELS else []
    if isinstance(node, ast.IfExp):
        return (levels_of(node.body, mod, consts, line, depth + 1)
                + levels_of(node.orelse, mod, consts, line, depth + 1))
    if isinstance(node, ast.Name):
        found = levels_of(_lookup(consts, node.id, line), mod, consts, line, depth + 1)
        if found:
            return found
    return LEVEL_RE.findall(ast.get_source_segment(mod.src, node) or "")


def _ordered_levels(found: list[str]) -> list[str]:
    return [lvl for lvl in LEVELS if lvl in found]


def slug(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return out[:SLUG_MAX].rstrip("-") or "unnamed"


# ---- the lint tool: the level is the list the finding lands in ---------------

def _assigned(func: ast.FunctionDef) -> dict[str, ast.AST]:
    """{name: value expression} for plain and tuple-unpacking assignments."""
    out: dict[str, ast.AST] = {}
    for node in ast.walk(func):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name):
            out.setdefault(target.id, node.value)
        elif isinstance(target, ast.Tuple):
            for element in target.elts:
                if isinstance(element, ast.Name):
                    out.setdefault(element.id, node.value)
    return out


def lint_levels(tree: ast.Module) -> tuple[dict[str, str], dict[int, str]]:
    """({function: level}, {line: level}) from `failures = [...]` / `warnings = [...]`
    in the assembly function - the lint findings carry no level of their own. A finding
    built inside the bucket expression is levelled by its line; one returned by a helper
    is levelled by that helper's name, whether it is spliced in directly or through a
    local (`sentence_findings, stats = _check_sentences(...)`)."""
    by_func: dict[str, str] = {}
    by_line: dict[int, str] = {}
    for func in (n for n in tree.body if isinstance(n, ast.FunctionDef)):
        produced = _assigned(func)
        for bucket, level in (("failures", "FAIL"), ("warnings", "WARN")):
            if bucket not in produced:
                continue
            sources = [produced[bucket]] + [produced[n.id]
                                            for n in ast.walk(produced[bucket])
                                            if isinstance(n, ast.Name) and n.id in produced]
            for call in (c for s in sources for c in _calls(s)):
                if not isinstance(call.func, ast.Name):
                    continue
                by_func.setdefault(call.func.id, level)
                by_line.setdefault(call.lineno, level)
    return by_func, by_line


# ---- doc citations ----------------------------------------------------------

CITE_RE = re.compile(r"""
    (?P<docbeat>\bdoc\s+(?P<db_doc>\d{2})\s+beats?\s+(?P<db_n>\d+))
  | (?P<beat>\b(?P<b_doc>\d{2})\s+B(?P<b_n>\d+)\b)
  | (?P<docsec>\bdoc\s+(?P<ds_doc>\d{2})\s+(?:sec|s)\s*(?P<ds_sec>\d+(?:\.\d+)?)\b)
  | (?P<docmisc>\bdoc\s+(?P<dm_doc>\d{2})\s+(?:rule|phase|Pillar|pillar)\s+\d+)
  | (?P<doconly>\bdoc\s+(?P<do_doc>\d{2})\b)
  | (?P<numsec>\b(?P<ns_doc>\d{2})\s+s(?P<ns_sec>\d+(?:\.\d+)?)\b)
  | (?P<dotted>\b(?P<dt_doc>\d{2})\.(?P<dt_sec>\d+)\b)
  | (?P<baresec>\bs(?P<bs_sec>\d+\.\d+)\b)
  | (?P<map>\bMAP\s+(?:sec|s)\s*(?P<map_sec>\d+)\b)
  | (?P<phase>\bP(?P<ph_n>[1-6])(?:\.md)?(?:\s+(?P<ph_sub>B\d+|QC))?\b)
  | (?P<ruling>\bE(?P<r_n>\d{2})\b)
  | (?P<check>\bCHECK-RESPONSIBILITIES(?:\s+s(?P<ck_sec>\d+))?)
""", re.X)
MAP_REL = "docs/content-video-engine/patterns/FULL-VIDEO-MAP.md"
PHASE_REL = "docs/content-video-engine/patterns/phase-guides/%s.md"
RULINGS_REL = "docs/portable/OPERATOR-RULINGS.md"
CHECK_REL = "docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md"


def load_docs_index(root: Path) -> list[dict]:
    path = Path(root) / DOCS_INDEX_REL
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _heading_hit(rows: list[dict], prefix: str) -> dict | None:
    """The first heading that starts with `prefix` as a whole section number. A leading
    section sign is stripped first - doc 37 numbers two of its sections as `S8`."""
    pat = re.compile(r"^" + re.escape(prefix) + r"(?=$|[^\d.]|\.(?!\d))")
    return next((r for r in rows if pat.match(r["heading"].strip().lstrip("§#").strip())), None)


def _doc_rows(index: list[dict], doc: str) -> list[dict]:
    return [r for r in index if r.get("doc") == doc]


def _path_rows(index: list[dict], rel: str) -> list[dict]:
    return [r for r in index if r["path"] == rel]


def _resolve_doc(index: list[dict], doc: str, section: str | None,
                 heading: str | None = None) -> tuple[str | None, int | None]:
    rows = _doc_rows(index, doc)
    if not rows:
        return None, None
    hit = _heading_hit(rows, heading or section) if (heading or section) else None
    row = hit or rows[0]
    return row["path"], row["line"]


def _resolve_file(index: list[dict], rel: str, prefix: str | None) -> tuple[str | None, int | None]:
    rows = _path_rows(index, rel)
    if not rows:
        return None, None
    hit = _heading_hit(rows, prefix) if prefix else None
    row = hit or rows[0]
    return row["path"], row["line"]


def _resolve(match: re.Match, index: list[dict]) -> tuple[str | None, int | None, bool]:
    """(path, line, emit) for one citation match - `emit` is False for an ambiguous
    numeric form that did not resolve, which is a false positive, not a lost cite."""
    g = match.groupdict()
    if g["docbeat"]:
        return (*_resolve_doc(index, g["db_doc"], None, f"Beat {g['db_n']}"), True)
    if g["beat"]:
        return (*_resolve_doc(index, g["b_doc"], None, f"Beat {g['b_n']}"), True)
    if g["docsec"]:
        return (*_resolve_doc(index, g["ds_doc"], g["ds_sec"]), True)
    if g["docmisc"]:
        return (*_resolve_doc(index, g["dm_doc"], None), True)
    if g["doconly"]:
        return (*_resolve_doc(index, g["do_doc"], None), True)
    if g["numsec"]:
        return (*_resolve_doc(index, g["ns_doc"], g["ns_sec"]), True)
    if g["dotted"]:
        path, line = _resolve_doc(index, g["dt_doc"], f"{g['dt_doc']}.{g['dt_sec']}")
        exact = line is not None and _heading_hit(_doc_rows(index, g["dt_doc"]),
                                                  f"{g['dt_doc']}.{g['dt_sec']}") is not None
        return (path, line, exact) if exact else (None, None, False)
    if g["baresec"]:
        hits = [r for r in index if _heading_hit([r], g["bs_sec"])]
        docs = {r["path"] for r in hits}
        return (hits[0]["path"], hits[0]["line"], True) if len(docs) == 1 else (None, None, False)
    if g["map"]:
        return (*_resolve_file(index, MAP_REL, g["map_sec"]), True)
    if g["phase"]:
        sub = g["ph_sub"]
        prefix = f"Beat {sub[1:]}" if sub and sub.startswith("B") else ("QC" if sub else None)
        return (*_resolve_file(index, PHASE_REL % f"P{g['ph_n']}", prefix), True)
    if g["ruling"]:
        return (*_resolve_file(index, RULINGS_REL, f"E{g['r_n']}"), True)
    return (*_resolve_file(index, CHECK_REL, g["ck_sec"]), True)


def find_cites(rule: str, index: list[dict]) -> list[dict]:
    """Every doc citation in a rule text, in order, deduplicated by reference."""
    out: list[dict] = []
    seen: set[str] = set()
    for match in CITE_RE.finditer(rule):
        ref = " ".join(match.group(0).split())
        if ref in seen:
            continue
        path, line, emit = _resolve(match, index)
        if not emit:
            continue
        seen.add(ref)
        out.append({"ref": ref, "path": path, "line": line})
    return out


# ---- tests ------------------------------------------------------------------

def read_tests(root: Path) -> list[tuple[str, str]]:
    tests = Path(root) / TESTS_REL
    if not tests.is_dir():
        return []
    files = sorted((p for p in tests.rglob("*.py") if "__pycache__" not in p.parts),
                   key=lambda p: p.as_posix())
    return [(p.name, p.read_text(encoding="utf-8", errors="replace")) for p in files]


def tests_naming(token: str, sources: list[tuple[str, str]]) -> list[str]:
    pat = re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")
    return sorted({name for name, text in sources if pat.search(text) or pat.search(name)})


# ---- extraction -------------------------------------------------------------

@dataclass(frozen=True)
class Raw:
    tool: str
    line: int
    family: str
    ident: str | None        # the row's own id, when it declares one
    code: str | None         # a failure NAME (the lint findings) - an id by another route
    rule: str
    levels: tuple[str, ...]
    token: str               # what a test would mention: the id, the code, else the rule


def _family_of(tool: str, func: str) -> str:
    base = FAMILY[tool]
    if base != "opening":
        return base
    return OPENING_FAMILY.get(func, OPENING_SHARED)


def _arg_nodes(call: ast.Call, roles: tuple[str | None, ...]) -> dict[str, ast.AST]:
    return {role: call.args[pos]
            for pos, role in enumerate(roles)
            if role and pos < len(call.args)}


def tool_rows(mod: Module, tool: str) -> tuple[list[Raw], list[str]]:
    """Every row a checker can emit, plus the call sites that could not be parsed."""
    types = row_types(mod.tree)
    helpers = emitters(mod.tree, types)
    consts = bindings(mod.tree)
    funcs = top_functions(mod.tree)
    by_func, by_line = lint_levels(mod.tree)
    rows: list[Raw] = []
    unparsed: list[str] = []
    for call in _calls(mod.tree):
        if not isinstance(call.func, ast.Name):
            continue
        roles = types.get(call.func.id) or _emitter_roles(helpers, call.func.id, call.lineno)
        if roles is None:
            continue
        args = _arg_nodes(call, roles)
        ident = rule_text(args.get("id"), mod, consts, call.lineno)
        code = rule_text(args.get("code"), mod, consts, call.lineno)
        # a tool with no rule field (the lint findings) states its rule in the message
        node = args["rule"] if "rule" in args else args.get("message")
        rule = rule_text(node, mod, consts, call.lineno)
        if rule is None:
            if ident is not None or code is not None:   # a row whose rule text did not read
                unparsed.append(f"{tool}:{call.lineno}")
            continue                                    # else: the emitter's own constructor
        func = enclosing(funcs, call.lineno)
        levels = levels_of(args.get("level"), mod, consts, call.lineno)
        if not levels:                             # no level argument: the list it lands in
            levels = [by_line.get(call.lineno) or by_func.get(func, "")]
        rows.append(Raw(tool, call.lineno, _family_of(tool, func), ident, code, rule,
                        tuple(_ordered_levels(levels)), ident or code or rule))
    return rows, unparsed


def _emitter_roles(helpers: list[Emitter], name: str, line: int) -> tuple[str | None, ...] | None:
    hits = [e for e in helpers if e.name == name]
    if not hits:
        return None
    before = [e for e in hits if e.line <= line]
    return (before[-1] if before else hits[0]).roles


# ---- the registry -----------------------------------------------------------

def build(repo_root: Path = REPO) -> list[dict]:
    """Every gate record, sorted by (family, id, rule). Nothing is imported or run."""
    root = Path(repo_root)
    index = load_docs_index(root)
    sources = read_tests(root)
    records: dict[tuple[str, str, str], dict] = {}
    for tool in sorted(FAMILY):
        path = root / SCRIPTS_REL / tool
        if not path.is_file():
            continue
        rows, _ = tool_rows(_parse(path, tool), tool)
        for row in rows:
            base = FAMILY[row.tool].split("-")[0]
            ident = row.ident or f"{base}:{slug(row.code or row.rule)}"
            key = (row.family, ident, row.rule)
            record = records.get(key)
            if record is None:
                records[key] = {
                    "id": ident, "tool": row.tool, "family": row.family, "rule": row.rule,
                    "levels": list(row.levels),
                    "cites": find_cites(row.rule, index),
                    "tests": tests_naming(row.token, sources),
                    "source": {"path": f"{SCRIPTS_REL}/{row.tool}", "line": row.line},
                }
                continue
            record["levels"] = _ordered_levels(record["levels"] + list(row.levels))
            record["source"]["line"] = min(record["source"]["line"], row.line)
    return [records[k] for k in sorted(records)]


def unparsed_calls(repo_root: Path = REPO) -> list[str]:
    """`tool:line` for every call site whose rule argument could not be read."""
    out: list[str] = []
    for tool in sorted(FAMILY):
        path = Path(repo_root) / SCRIPTS_REL / tool
        if path.is_file():
            out += tool_rows(_parse(path, tool), tool)[1]
    return sorted(out)


# ---- the composition block --------------------------------------------------

def _func(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    return next((n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == name), None)


def _comment_lines(mod: Module) -> dict[int, str]:
    """{line: comment} for the whole module - tokenized, so a trailing comment counts."""
    out: dict[int, str] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(mod.src).readline):
            if tok.type == tokenize.COMMENT:
                out[tok.start[0]] = tok.string.strip()
    except (tokenize.TokenError, IndentationError):          # unreadable source: no comments
        return {}
    return out


def _step_tool(mod: Module, name: str) -> str | None:
    """The checker a runner step reports as, from its own `ToolResult("<tool>", ...)`."""
    step = _func(mod.tree, name)
    if step is None:
        return None
    return next((c.args[0].value for c in _calls(step)
                 if isinstance(c.func, ast.Name) and c.func.id == "ToolResult"
                 and c.args and isinstance(c.args[0], ast.Constant)), None)


def composition(repo_root: Path = REPO) -> list[str]:
    """What the runner runs, in what order, and how short/long routes - quoted, never
    paraphrased: the order comes from `run_all`, the routing from `is_short`'s docstring
    and the comments inside the steps."""
    path = Path(repo_root) / SCRIPTS_REL / RUNNER
    if not path.is_file():
        return [f"`{SCRIPTS_REL}/{RUNNER}` not found in this checkout.", ""]
    mod = _parse(path, RUNNER)
    run_all = _func(mod.tree, "run_all")
    steps = [(c.func.id, _step_tool(mod, c.func.id)) for c in (_calls(run_all) if run_all else [])
             if isinstance(c.func, ast.Name) and _step_tool(mod, c.func.id)]
    out = [f"`{RUNNER}` runs the checkers in this order (`run_all`):", ""]
    out += [f"{i}. `{name}()` -> `{tool}`" for i, (name, tool) in enumerate(steps, start=1)]
    out += ["", "Short or long is decided once, in `is_short`:", ""]
    doc = ast.get_docstring(_func(mod.tree, "is_short") or ast.Module(body=[], type_ignores=[])) or ""
    out += ["> " + " ".join(line.split()) for line in doc.splitlines() if line.strip()]
    out += ["", "The routing comments, verbatim from the runner:", ""]
    comments = _comment_lines(mod)
    for name, _ in steps:
        func = _func(mod.tree, name)
        span = range(func.lineno, (func.end_lineno or func.lineno) + 1) if func else range(0)
        out += [f"> `{name}`: {comments[ln]}" for ln in span if ln in comments]
    return out + [""]


# ---- rendering --------------------------------------------------------------

def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def _cites_text(cites: list[dict]) -> str:
    if not cites:
        return "none"
    return ", ".join(f"{c['ref']} -> " + (f"{c['path']}:{c['line']}" if c["path"] else "unresolved")
                     for c in cites)


def _line(record: dict) -> str:
    return (f"- **{record['id']}** - {record['rule']}"
            f" - levels: {', '.join(record['levels']) or 'none'}"
            f" - cites: {_cites_text(record['cites'])}"
            f" - tests: {', '.join(record['tests']) or 'none'}"
            f" - {record['tool']}:{record['source']['line']}")


def render_md(records: list[dict], repo_root: Path = REPO) -> str:
    ids = {r["id"] for r in records}
    head = [
        "# GATES-REGISTRY - every speech-writing gate, from the code that enforces it",
        "",
        f"Generated by `{BUILD_CMD}`. Do not hand-edit it: `--check` fails when it drifts",
        "from the tools. The rule text, the levels, the doc citations and the tests are read",
        "out of the checkers' source by `ast` - the tools are never imported or executed.",
        "",
        "The recipe - one call:",
        "",
        "```bash",
        f'rg -i "<id or phrase>" {MD_REL}',
        "```",
        "",
        "Each line is: id - rule text - the levels the call can emit - doc citations resolved",
        f"against `{DOCS_INDEX_REL}` - the tests that name the id - and the source line.",
        "An f-string rule keeps its placeholders as `{expr}`, and `{NAME=value}` when the",
        "placeholder is a literal constant of the tool, so a threshold is greppable both ways.",
        "A gate whose rule text differs between branches has one line per distinct rule text.",
        "",
        f"{len(records)} records, {len(ids)} distinct ids, across {len(FAMILY)} checkers.",
        "",
    ]
    body: list[str] = []
    for family in FAMILIES:
        rows = [r for r in records if r["family"] == family]
        body += [f"## {family}", ""]
        body += [_line(r) for r in rows] or ["- (no rows of its own - see **Composition**)"]
        body.append("")
    body += ["## Composition", ""] + composition(repo_root)
    return "\n".join(head + body)


def rendered(repo_root: Path = REPO) -> dict[str, str]:
    records = build(repo_root)
    return {JSONL_REL: render_jsonl(records), MD_REL: render_md(records, repo_root)}


def write(repo_root: Path = REPO) -> int:
    for rel, text in rendered(repo_root).items():
        path = Path(repo_root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return len(build(repo_root))


def check(repo_root: Path = REPO) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty = in sync."""
    problems: list[str] = []
    for rel, want in rendered(repo_root).items():
        path = Path(repo_root) / rel
        if not path.is_file():
            problems.append(f"{rel} (missing)")
            continue
        have = path.read_text(encoding="utf-8")
        if have == want:
            continue
        diff = list(difflib.ndiff(have.splitlines(), want.splitlines()))
        added = sum(1 for d in diff if d.startswith("+ "))
        removed = sum(1 for d in diff if d.startswith("- "))
        problems.append(f"{rel} (+{added}/-{removed} lines)")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    root = args.repo.resolve()
    if args.write:
        count = write(root)
        by_family = {f: sum(1 for r in build(root) if r["family"] == f) for f in FAMILIES}
        print(f"build_gates_registry: {count} record(s) -> {JSONL_REL} + {MD_REL}")
        print("build_gates_registry: " + ", ".join(f"{f}={n}" for f, n in by_family.items()))
    stale = check(root)
    if stale:
        print("build_gates_registry: STALE - " + "; ".join(stale) + " - run --write")
        return 1
    records = build(root)
    cited = [c for r in records for c in r["cites"]]
    print(f"build_gates_registry: in sync ({len(records)} records, "
          f"{len({r['id'] for r in records})} ids, "
          f"{sum(1 for c in cited if c['path'])}/{len(cited)} cites resolved)")
    missed = unparsed_calls(root)
    if missed:
        print("build_gates_registry: unparsed call site(s) - " + ", ".join(missed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
