"""T19 pure page-surface geometry.

The module is intentionally tested through Node, the same runtime that will later consume it from the player. These
tests cover the measured registered quad, the actual caller-supplied destination profile shape, and seek-order
invariance without importing or changing the renderer/compiler.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MODULE = (ROOT / "content/video_engine/scripts/kinetics/page_surface.mjs").resolve()
HOMOGRAPHY = (ROOT / "content/video_engine/scripts/kinetics/homography.mjs").resolve()
NODE = shutil.which("node") or shutil.which("node.exe")

QUAD = [[0.305622, 0.185972], [0.693182, 0.187035], [0.693182, 0.407014], [0.305622, 0.407014]]
STAGE = {"w": 1920, "h": 1080}
# The current Fed dense-line phone profile, passed as geometry rather than copied into the helper.
DESTINATION = {"x": 57.6, "y": 196.992, "w": 1808.072574685714, "h": 747.036, "vw": 1355.384, "vh": 560}


def _assert_quad_close(got: list[list[float]], want: list[list[float]], abs_tol: float) -> None:
    assert len(got) == len(want)
    for actual, expected in zip(got, want):
        assert actual == pytest.approx(expected, abs=abs_tol)


def _node(expression: str):
    """Evaluate one JSON-producing expression against the real ESM modules."""
    if not NODE:
        pytest.skip("node is not on PATH")
    source = (
        f"import * as P from {json.dumps(MODULE.as_uri())};\n"
        f"import {{ hApply }} from {json.dumps(HOMOGRAPHY.as_uri())};\n"
        f"console.log(JSON.stringify({expression}));\n"
    )
    proc = subprocess.run([NODE, "--input-type=module", "-e", source], capture_output=True, text=True)
    if proc.returncode:
        raise AssertionError(f"node failed ({proc.returncode}): {proc.stderr}\n{source}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _node_error(expression: str) -> str:
    if not NODE:
        pytest.skip("node is not on PATH")
    source = (
        f"import * as P from {json.dumps(MODULE.as_uri())};\n"
        f"try {{ {expression}; console.log('NO_ERROR'); }} catch (error) {{ console.log(String(error)); process.exitCode = 0; }}\n"
    )
    proc = subprocess.run([NODE, "--input-type=module", "-e", source], capture_output=True, text=True, check=True)
    return proc.stdout.strip().splitlines()[-1]


def _fixture_expression() -> str:
    return f"P.surfacePlotGeometry({json.dumps(QUAD)}, {json.dumps(STAGE)})"


def _frames_expression(times: list[float], destination: dict = DESTINATION) -> str:
    return (
        f"(() => {{ const s={_fixture_expression()}, d={json.dumps(destination)}, ts={json.dumps(times)}; "
        "const ratio=(J)=>{const a=J[0]**2+J[2]**2,b=J[1]**2+J[3]**2,c=J[0]*J[1]+J[2]*J[3],tr=a+b,det=a*b-c*c,disc=Math.max(0,tr*tr-4*det);return Math.sqrt((tr+Math.sqrt(disc))/(tr-Math.sqrt(disc)));}; "
        "return ts.map(t=>{const g=P.surfaceGeometryAt(s,d,t), x=g.hostW/2, y=g.hostH/2, e=1e-3, p=hApply(g.matrix,x,y), px=hApply(g.matrix,x+e,y), py=hApply(g.matrix,x,y+e); "
        "const J=[(px[0]-p[0])/e,(py[0]-p[0])/e,(px[1]-p[1])/e,(py[1]-p[1])/e]; "
        "const corners=[[0,0],[g.hostW,0],[g.hostW,g.hostH],[0,g.hostH]].map(([cx,cy])=>hApply(g.matrix,cx,cy)); "
        "const cornerError=Math.max(...corners.map((q,i)=>Math.hypot(q[0]-g.quad[i][0],q[1]-g.quad[i][1]))); "
        "return {t,progress:g.progress,eased:g.eased,quad:g.quad,hostW:g.hostW,hostH:g.hostH,chart:g.chart,viewBox:g.viewBox,aspect:g.chartAspect/g.viewBoxAspect,cornerError,jacobianAnisotropy:ratio(J)};}); })()"
    )


def test_source_stage_quad_and_native_host_match_measured_surface():
    source = _node(_fixture_expression())
    _assert_quad_close(
        source["quad"],
        [[586.79424, 200.84976], [1330.90944, 201.9978], [1330.90944, 439.57512], [586.79424, 439.57512]],
        1e-9,
    )
    assert source["hostW"] == pytest.approx(744.115642806, abs=1e-9)
    assert source["hostH"] == pytest.approx(238.15134, abs=1e-9)
    assert source["viewW"] == pytest.approx(1749.747702328, abs=1e-9)
    assert source["viewH"] == 560
    assert source["chart"]["w"] / source["chart"]["h"] == pytest.approx(
        source["viewBox"]["w"] / source["viewBox"]["h"], abs=1e-12
    )


def test_corners_aspect_and_jacobian_hold_across_the_grow():
    frames = _node(_frames_expression([0, 0.1125, 0.225, 0.3375, 0.45]))
    assert max(frame["cornerError"] for frame in frames) <= 0.01
    assert max(abs(frame["aspect"] - 1) for frame in frames) <= 0.001
    assert max(frame["jacobianAnisotropy"] for frame in frames) <= 1.02
    _assert_quad_close(frames[0]["quad"], _node(_fixture_expression())["quad"], 1e-12)
    assert frames[-1]["quad"] == [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]


def test_endpoints_are_exact_and_progress_is_bounded():
    result = _node(
        f"(() => {{ const s={_fixture_expression()}, d={json.dumps(DESTINATION)}, pick=t=>P.surfaceGeometryAt(s,d,t); "
        "const shape=g=>({quad:g.quad,hostW:g.hostW,hostH:g.hostH,matrix:g.matrix,chart:g.chart,viewBox:g.viewBox}); "
        "return {before:shape(pick(-2)),start:shape(pick(0)),end:shape(pick(0.45)),after:shape(pick(2)),progress:[pick(-2).progress,pick(0).progress,pick(0.45).progress,pick(2).progress]}; })()"
    )
    assert result["before"] == result["start"]
    assert result["after"] == result["end"]
    assert result["progress"] == [0, 0, 1, 1]
    assert result["end"]["chart"] == {"x": DESTINATION["x"], "y": DESTINATION["y"], "w": DESTINATION["w"], "h": DESTINATION["h"]}
    assert result["end"]["viewBox"] == {"x": 0, "y": 0, "w": DESTINATION["vw"], "h": DESTINATION["vh"]}


def test_cold_and_reverse_seek_orders_are_identical():
    times = [0, 0.05, 0.225, 0.4, 0.45, 0.12]
    result = _node(
        f"(() => {{ const s={_fixture_expression()}, d={json.dumps(DESTINATION)}, order={json.dumps(times)}, rev=[...order].reverse(); "
        "const shape=t=>P.surfaceGeometryAt(s,d,t), key=t=>JSON.stringify(shape(t)); "
        "const canonical=list=>[...new Set(list)].sort((a,b)=>a-b).map(t=>[t,key(t)]); return canonical(order).toString()===canonical(rev).toString(); })()"
    )
    assert result is True


def test_destination_geometry_is_caller_supplied_not_a_baked_page_layout():
    destination = {"x": 91, "y": 73, "w": 1250, "h": 500, "vw": 1400, "vh": 560}
    end = _node(
        f"P.surfaceGeometryAt({_fixture_expression()}, {json.dumps(destination)}, 0.45)"
    )
    assert end["chart"] == {"x": 91, "y": 73, "w": 1250, "h": 500}
    assert end["viewBox"] == {"x": 0, "y": 0, "w": 1400, "h": 560}
    assert end["chart"] != {"x": 57.6, "y": 196.992, "w": 1334.016, "h": 747.036}


@pytest.mark.parametrize(
    "expression,needle",
    [
        ("P.surfacePlotGeometry([[0,0],[1,0],[1,1]], {w:1920,h:1080})", "four"),
        ("P.surfacePlotGeometry([[0,0],[1,0],[1,1],[0,0]], {w:1920,h:1080})", "repeat"),
        ("P.surfaceGeometryAt(P.surfacePlotGeometry([[0,0],[1,0],[1,1],[0,1]], {w:1920,h:1080}), {x:0,y:0,w:100,h:50,vw:100,vh:560}, 'seek')", "time"),
        ("P.surfaceGeometryAt(P.surfacePlotGeometry([[0,0],[1,0],[1,1],[0,1]], {w:1920,h:1080}), {x:0,y:0,w:100,h:50,vw:100,vh:560}, 0, {duration:0})", "duration"),
        ("P.surfaceGeometryAt(P.surfacePlotGeometry([[0,0],[1,0],[1,1],[0,1]], {w:1920,h:1080}), {x:0,y:0,w:100,h:50,vw:100,vh:540}, 0)", "viewH"),
    ],
)
def test_nonfinite_or_invalid_geometry_and_timing_are_refused(expression: str, needle: str):
    assert needle in _node_error(expression)
