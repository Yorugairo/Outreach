# The docs layers, timed - 2026-09-16 (P63)

The evidence behind P63's Summary: `build_docs_layers.py --check`, one layer at a time, on the main checkout the morning
the operator named the dual bottleneck; then the animation registry's profile. Every commit paid the whole check through
`~/.claude/hooks/context_guard.py`; 60 of the last 60 commits rewrote generated layers (15 MB tracked).

## Per-layer `--check` before P63 (91 s)

```
docs-index              1.7s  exit=1  build_docs_index: STALE - docs/DOCS-INDEX.jsonl (+26/-26 lines); docs/DOCS-INDEX.md (+26/-
capabilities-index      0.2s  exit=0  build_capabilities_index: in sync (187 records, 3 flagged, 0 failed)
asset-index             0.1s  exit=0  build_asset_index: in sync (73 assets)
research-ledger         0.3s  exit=1  build_research_ledger: STALE - docs/RESEARCH-LEDGER.jsonl (+3/-3 lines); docs/RESEARCH-LED
effects-catalog         0.5s  exit=1  build_effects_catalog: STALE - docs/EFFECTS-CATALOG.jsonl (+1/-1 lines); docs/EFFECTS-CATA
docs-manifest           1.1s  exit=0  build_docs_manifest: in sync (482 documents, 75834 bytes of Markdown)
topic-index             2.5s  exit=1  build_topic_index: STALE - docs/DOCS-CITATIONS.jsonl (+167/-123 lines); docs/DOCS-TOPICS.m
gates-registry         14.9s  exit=0  build_gates_registry: in sync (163 records, 149 ids, 199/199 cites resolved)
animation-registry     67.7s  exit=1  build_animation_registry: STALE - docs/ANIMATION-REGISTRY.jsonl (+271/-271 lines); docs/AN
craft-map               0.9s  exit=0  build_craft_map: in sync (81 devices, 53 gated, 32 judge-only, 181/181 definitions resolve
doc-overlap             0.8s  exit=1  report_doc_overlap: STALE - docs/DOC-OVERLAP.jsonl (+12/-12 lines); docs/DOC-OVERLAP.md (+
TOTAL check 90.8s
```

## `build_animation_registry.py --check` under cProfile (219 s; 68 s plain)

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     23/1    0.000    0.000  218.781  218.781 {built-in method builtins.exec}
        1    0.000    0.000  218.781  218.781 build_animation_registry.py:1(<module>)
        1    0.001    0.001  218.757  218.757 build_animation_registry.py:819(main)
        1    0.003    0.003  218.747  218.747 build_animation_registry.py:792(check)
        1    0.004    0.004  210.743  210.743 build_animation_registry.py:778(rendered)
        1    0.000    0.000  210.726  210.726 build_animation_registry.py:757(build)
        1    0.004    0.004  152.453  152.453 build_animation_registry.py:584(apply_status)
      402    0.006    0.000  139.676    0.347 build_animation_registry.py:606(code_status)
      183    1.385    0.008  138.023    0.754 build_animation_registry.py:644(key_uses)
     3294   80.031    0.024  123.828    0.038 build_animation_registry.py:619(code_lines_only)
        1    0.003    0.003   57.105   57.105 build_animation_registry.py:423(code_records)
      402    0.002    0.000   57.032    0.142 build_animation_registry.py:455(code_record)
15121622/15005442   15.318    0.000   45.471    0.000 {built-in method builtins.any}
  8302616    2.783    0.000   42.509    0.000 build_animation_registry.py:297(in_spans)
      402    1.687    0.004   36.762    0.091 build_animation_registry.py:473(template_sites)
378626525   26.994    0.000   26.994    0.000 {method 'startswith' of 'str' objects}
259637215   26.395    0.000   26.395    0.000 build_animation_registry.py:298(<genexpr>)
  5062236   26.184    0.000   26.184    0.000 {method 'search' of 're.Pattern' objects}
      219    0.002    0.000   26.066    0.119 build_animation_registry.py:441(key_records)
      402    0.002    0.000   20.267    0.050 build_animation_registry.py:486(test_files)
      402    0.046    0.000   20.260    0.050 build_animation_registry.py:488(<listcomp>)
      352    0.002    0.000   11.290    0.032 build_animation_registry.py:682(formula_status)
263990936/263981228   11.085    0.000   11.087    0.000 {built-in method builtins.len}
```

## After

| step | before | after |
| --- | --- | --- |
| `build_docs_layers.py --check`, nothing changed | 91 s | 0.7-1.0 s (a digest comparison) |
| `build_animation_registry.py --check` | 64-68 s | 2.4 s (3.4 s with the ndiff on a stale tree), byte-identical output |
| one touched docs file -> the layers current again | a full `--write` (~3.5 min) | `--check` names the stale layer in 0.55 s; `--ensure` rebuilds the nine downstream in 27 s |
| a `git commit` | the 91 s check, refused if ANY lane's edit made a layer stale | no layers check at all |
| `docs_find.py` on a current tree | 0.12 s | 0.73 s (the digest) |
| generated text in git | 15 MB, rewritten 60/60 commits | none (24 outputs untracked; `DOCS-INDEX.config.json` stays) |
