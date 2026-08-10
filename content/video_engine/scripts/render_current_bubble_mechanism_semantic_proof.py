"""Render the approved first-90-second semantic finance proof.

This is deliberately a bounded review renderer, not the full-episode path. It
uses the canonical narration clock, the approved cue roles, deterministic
numeric surfaces, and only the assets named in the first-90s proof plan.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
OUT = PROJECT / "animatic/revisions/semantic-proof-v2"
WIDTH, HEIGHT, FPS, DURATION = 1280, 720, 24, 89.803
FONT = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")


@dataclass(frozen=True)
class State:
    start: float
    end: float
    asset: str
    focus: tuple[float, float]
    overlay: str | None = None
    exit_vector: tuple[float, float] = (0.0, 0.0)


ASSETS = PROJECT / "assets"
STATE = [
    State(0.000, 2.403, "review/semantic-wave-01/wrong-bubble-elevators-v2.png", (0.50, 0.50), exit_vector=(1, 0)),
    State(2.403, 4.900, "review/semantic-wave-01/memory-skepticism-v2.png", (0.43, 0.47), exit_vector=(1, 0)),
    State(4.900, 7.442, "review/semantic-wave-01/memory-skepticism-v2.png", (0.66, 0.57), "returns", (0, 1)),
    State(7.442, 11.610, "review/semantic-wave-03/default-bubble-reaction-v1.png", (0.52, 0.50), exit_vector=(1, 0)),
    State(11.610, 15.452, "review/semantic-wave-01/memory-three-supports-v1.png", (0.46, 0.53), exit_vector=(1, 0)),
    State(15.452, 19.075, "review/semantic-wave-01/memory-three-supports-v1.png", (0.65, 0.53), exit_vector=(1, 0)),
    State(19.075, 23.034, "review/semantic-wave-01/memory-three-supports-v1.png", (0.76, 0.52), exit_vector=(1, 0)),
    State(23.034, 28.606, "review/semantic-wave-01/index-fund-weighted-inflows-v2.png", (0.42, 0.49), exit_vector=(1, 0)),
    State(28.606, 31.950, "review/semantic-wave-01/index-fund-weighted-inflows-v2.png", (0.59, 0.48), exit_vector=(1, 0)),
    State(31.950, 37.720, "review/semantic-wave-01/index-fund-weighted-inflows-v2.png", (0.70, 0.57), "top_ten", (-1, 1)),
    State(37.720, 41.750, "review/semantic-wave-01/memory-three-supports-v1.png", (0.54, 0.62), "risk", (0, 1)),
    State(41.750, 45.766, "review/semantic-wave-02/bottleneck-repricing-v1.png", (0.55, 0.58), "risk_hold", (1, 0)),
    State(45.766, 49.853, "review/semantic-wave-02/bottleneck-repricing-v1.png", (0.52, 0.48), exit_vector=(1, 0)),
    State(49.853, 51.920, "review/semantic-wave-02/bottleneck-repricing-v1.png", (0.68, 0.55), exit_vector=(-1, 0)),
    State(51.920, 58.038, "review/semantic-wave-02/safe-default-inspection-v1.png", (0.52, 0.50), exit_vector=(0, 1)),
    State(58.038, 61.579, "review/semantic-wave-02/safe-default-inspection-v1.png", (0.48, 0.48), "diagnostic_reveal", (1, 0)),
    State(61.579, 64.876, "review/semantic-wave-02/safe-default-inspection-v1.png", (0.66, 0.48), "diagnostic_hold", (1, 0)),
    State(64.876, 68.731, "review/semantic-wave-02/belief-versus-support-v2.png", (0.36, 0.52), exit_vector=(1, 0)),
    State(68.731, 71.784, "review/semantic-wave-02/belief-versus-support-v2.png", (0.64, 0.52), exit_vector=(0, 1)),
    State(71.784, 75.870, "review/semantic-wave-02/belief-versus-support-v2.png", (0.50, 0.54), exit_vector=(1, 0)),
    State(75.870, 78.935, "review/semantic-wave-01/wrong-bubble-elevators-v2.png", (0.38, 0.52), exit_vector=(1, 0)),
    State(78.935, 82.767, "review/semantic-wave-01/wrong-bubble-elevators-v2.png", (0.62, 0.52), exit_vector=(0, 1)),
    State(82.767, 86.169, "review/semantic-wave-01/wrong-bubble-elevators-v2.png", (0.50, 0.66), exit_vector=(-1, 0)),
    State(86.169, 89.803, "review/semantic-wave-01/wrong-bubble-elevators-v2.png", (0.50, 0.42), "callback", (0, 0)),
]


def font(size: int, *, regular: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_REGULAR if regular else FONT), size=size)


def cover(image: Image.Image, focus: tuple[float, float], progress: float, offset: tuple[float, float]) -> Image.Image:
    """A modest, motivated paper-theatre push with a swing cut offset."""
    zoom = 1.10 + (0.025 * progress)
    target_w = int(WIDTH * zoom)
    target_h = int(HEIGHT * zoom)
    fitted = ImageOps.fit(image.convert("RGB"), (target_w, target_h), method=Image.Resampling.LANCZOS)
    max_x, max_y = target_w - WIDTH, target_h - HEIGHT
    left = int(max(0, min(max_x, (focus[0] * target_w) - (WIDTH / 2) + offset[0])))
    top = int(max(0, min(max_y, (focus[1] * target_h) - (HEIGHT / 2) + offset[1])))
    return fitted.crop((left, top, left + WIDTH, top + HEIGHT)).convert("RGBA")


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int] | None = None) -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=3 if outline else 1)


def evidence_returns(frame: Image.Image) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    values = [("MU", "+685.7%", "#FFD06B"), ("KOSPI", "+93.9%", "#59D6E8"), ("S&P 500", "+22.4%", "#E9D8AF")]
    x, y = 78, 420
    for label, value, color in values:
        rounded(draw, (x, y, x + 255, y + 78), (5, 18, 31, 225), (220, 194, 128, 210))
        draw.text((x + 18, y + 12), label, font=font(22), fill=color)
        draw.text((x + 18, y + 39), value, font=font(28), fill=(255, 248, 224))
        x += 272
    draw.text((78, 510), "1Y through Aug. 7, 2026 • adjusted close", font=font(18, regular=True), fill=(244, 232, 194))


def evidence_top_ten(frame: Image.Image) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    rounded(draw, (820, 104, 1198, 200), (5, 18, 31, 225), (220, 194, 128, 220))
    draw.text((846, 121), "S&P 500 TOP 10", font=font(21), fill=(90, 214, 232))
    draw.text((846, 148), "almost 40%", font=font(37), fill=(255, 248, 224))


def risk_qualifiers(frame: Image.Image, progress: float, *, hold: bool = False) -> None:
    """Deterministic counterpart to memory-risk-qualifiers-v1.svg."""
    draw = ImageDraw.Draw(frame, "RGBA")
    cards = [("CORRECTION", "#D15B44"), ("OVERPRICED", "#D1963D"), ("CYCLICAL", "#2D9DB7")]
    x = 167
    for index, (label, accent) in enumerate(cards):
        if not hold and progress < (0.10 + (index * 0.25)):
            continue
        rounded(draw, (x, 312, x + 300, 438), (232, 215, 174, 242), (10, 41, 57, 240))
        draw.rounded_rectangle((x + 18, 332, x + 31, 418), radius=6, fill=accent)
        size = 26 if label != "OVERPRICED" else 23
        draw.text((x + 52, 358), label, font=font(size), fill=(19, 44, 59))
        x += 323


def bubble_diagnostic(frame: Image.Image, progress: float, *, hold: bool = False) -> None:
    """Deterministic counterpart to bubble-mechanism-diagnostic-v1.svg."""
    draw = ImageDraw.Draw(frame, "RGBA")
    cards = [
        (94, "SYMPTOM", ["PRICE MOVED"], (209, 91, 68, 255)),
        (670, "QUESTION", ["WHAT MOVED", "THE PRICE?"], (45, 157, 183, 255)),
    ]
    for index, (x, header, lines, color) in enumerate(cards):
        if not hold and progress < (0.12 + (index * 0.40)):
            continue
        rounded(draw, (x, 160, x + 514, 470), (232, 215, 174, 246), (11, 41, 57, 246))
        draw.rounded_rectangle((x, 160, x + 514, 224), radius=18, fill=color)
        draw.text((x + 28, 178), header, font=font(24), fill=(255, 249, 231))
        y = 294
        for line in lines:
            w = draw.textbbox((0, 0), line, font=font(40))[2]
            draw.text((x + (514 - w) / 2, y), line, font=font(40), fill=(19, 44, 59))
            y += 56
    if hold or progress >= 0.52:
        draw.line((624, 315, 653, 315), fill=(209, 150, 61, 255), width=14)
        draw.polygon([(653, 288), (683, 315), (653, 342)], fill=(209, 150, 61, 255))


def caption(frame: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    max_width = 1010
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font(31))[2] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    line_h = 42
    box_h = 28 + line_h * len(lines)
    box = (80, HEIGHT - box_h - 24, WIDTH - 80, HEIGHT - 24)
    rounded(draw, box, (2, 12, 23, 205))
    y = box[1] + 12
    for line in lines:
        w = draw.textbbox((0, 0), line, font=font(31))[2]
        draw.text(((WIDTH - w) / 2, y), line, font=font(31), fill=(255, 250, 237))
        y += line_h


def caption_chunks(words: list[dict[str, object]], duration: float) -> list[tuple[float, float, str]]:
    selected = [w for w in words if float(w["start_s"]) < duration]
    chunks, current = [], []
    for word in selected:
        current.append(word)
        token = str(word["w"])
        if len(current) >= 5 or token.endswith((".", "?", "!", ",", ";", ":")):
            chunks.append((float(current[0]["start_s"]), float(current[-1]["end_s"]), " ".join(str(v["w"]) for v in current)))
            current = []
    if current:
        chunks.append((float(current[0]["start_s"]), min(duration, float(current[-1]["end_s"])), " ".join(str(v["w"]) for v in current)))
    return chunks


def active_caption(chunks: list[tuple[float, float, str]], t: float) -> str:
    for start, end, text in chunks:
        if start <= t < end + 0.10:
            return text
    return ""


def find_state(t: float) -> tuple[int, State]:
    for index, state in enumerate(STATE):
        if state.start <= t < state.end:
            return index, state
    return len(STATE) - 1, STATE[-1]


def overlay_for(frame: Image.Image, name: str | None, progress: float) -> None:
    if name == "returns":
        evidence_returns(frame)
    elif name == "top_ten":
        evidence_top_ten(frame)
    elif name == "risk":
        risk_qualifiers(frame, progress)
    elif name == "risk_hold":
        risk_qualifiers(frame, progress, hold=True)
    elif name == "diagnostic_reveal":
        bubble_diagnostic(frame, progress)
    elif name == "diagnostic_hold":
        bubble_diagnostic(frame, progress, hold=True)
    elif name == "callback":
        draw = ImageDraw.Draw(frame, "RGBA")
        rounded(draw, (350, 112, 930, 194), (5, 18, 31, 220), (220, 194, 128, 220))
        label = "SAME VISIBLE MOVE • DIFFERENT MECHANISM"
        draw.text((389, 137), label, font=font(24), fill=(255, 246, 218))


def render() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    cue_sheet = json.loads((PROJECT / "audio/canonical/history_episode_1_master.words.json").read_text(encoding="utf-8"))
    captions = caption_chunks(cue_sheet["words"], DURATION)
    images: dict[str, Image.Image] = {}
    for state in STATE:
        images.setdefault(state.asset, Image.open(ASSETS / state.asset).convert("RGBA"))

    target = OUT / "current-bubble-mechanism-first-90s-semantic-proof-v2.mp4"
    ffmpeg = "ffmpeg"
    command = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
        "-i", str(PROJECT / "audio/canonical/history_episode_1_master.mp3"), "-t", f"{DURATION:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(target),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        frames = round(DURATION * FPS)
        for index in range(frames):
            t = index / FPS
            state_index, state = find_state(t)
            progress = (t - state.start) / max(0.001, state.end - state.start)
            swing_window = min(0.24, (state.end - state.start) * 0.18)
            offset = (0.0, 0.0)
            blur = 0.0
            if state_index and (t - state.start) < swing_window:
                ratio = (t - state.start) / swing_window
                previous_vector = STATE[state_index - 1].exit_vector
                inertia = (1.0 - ratio) ** 2
                offset = (-previous_vector[0] * 58 * inertia, -previous_vector[1] * 38 * inertia)
                blur = 1.5 * inertia
            elif (state.end - t) < swing_window and state.exit_vector != (0.0, 0.0):
                ratio = 1.0 - ((state.end - t) / swing_window)
                inertia = ratio**2
                offset = (state.exit_vector[0] * 58 * inertia, state.exit_vector[1] * 38 * inertia)
                blur = 1.5 * inertia
            frame = cover(images[state.asset], state.focus, progress, offset)
            if blur > 0.1:
                frame = frame.filter(ImageFilter.GaussianBlur(radius=blur))
            overlay_for(frame, state.overlay, progress)
            text = active_caption(captions, t)
            if text:
                caption(frame, text)
            process.stdin.write(frame.convert("RGB").tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("ffmpeg render failed")
    return target


if __name__ == "__main__":
    print(render())
