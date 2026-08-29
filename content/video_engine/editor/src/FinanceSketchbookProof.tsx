import React from "react";
import {
  Audio,
  type CalculateMetadataFunction,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {
  FinanceSketchbookProofProps,
  FinanceSketchbookSourceCard,
  FinanceSketchbookState,
  FinanceSketchbookStateId,
} from "./types";

const COLORS = {
  paper: "#FFF8EA",
  ink: "#111820",
  blue: "#A9DDF4",
  blueDark: "#2E638C",
  yellow: "#FFD166",
  red: "#F16B63",
  redDark: "#A93636",
  green: "#76C997",
  greenDark: "#2C7A55",
  lilac: "#C5B5F2",
  gray: "#D7D6D1",
  white: "#FFFDF7",
};

const VIEWBOX = { width: 1920, height: 1080 };
const STATE_FALLBACKS: Record<FinanceSketchbookStateId, FinanceSketchbookState> = {
  "basket-product-qualities": { id: "basket-product-qualities", start_word_index: 1025, end_word_index: 1058, start_s: 410.26, end_s: 422.59, relative_start_s: 0, relative_end_s: 12.33 },
  "two-jobs": { id: "two-jobs", start_word_index: 1059, end_word_index: 1075, start_s: 422.834, end_s: 428.209, relative_start_s: 12.574, relative_end_s: 17.949 },
  concentration: { id: "concentration", start_word_index: 1076, end_word_index: 1121, start_s: 428.534, end_s: 444.335, relative_start_s: 18.274, relative_end_s: 34.075 },
  "shared-exposure": { id: "shared-exposure", start_word_index: 1122, end_word_index: 1155, start_s: 444.614, end_s: 459.614, relative_start_s: 34.354, relative_end_s: 49.354 },
  "long-tail": { id: "long-tail", start_word_index: 1156, end_word_index: 1170, start_s: 460.218, end_s: 464.223, relative_start_s: 49.958, relative_end_s: 53.963 },
  "admission-versus-weighting": { id: "admission-versus-weighting", start_word_index: 1171, end_word_index: 1188, start_s: 464.548, end_s: 470.992, relative_start_s: 54.288, relative_end_s: 60.732 },
};

const finite = (value: number | undefined, fallback: number): number =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

const clamp = (value: number, min = 0, max = 1): number => Math.min(max, Math.max(min, value));
const smoothstep = (value: number): number => {
  const t = clamp(value);
  return t * t * (3 - 2 * t);
};

const steppedTime = (frame: number, fps: number): number => {
  const step = Math.max(1, Math.round(fps / 12));
  return (Math.floor(frame / step) * step) / fps;
};

const progressBetween = (time: number, start: number, end: number): number => {
  if (time <= start) return 0;
  if (time >= end) return 1;
  return smoothstep((time - start) / Math.max(0.001, end - start));
};

const windowOpacity = (time: number, start: number, end: number, fade = 0.45): number => {
  const tolerance = 1 / 12;
  if (time < start - tolerance) return 0;
  const entrance = time <= start + tolerance ? 1 : progressBetween(time, start, start + fade);
  const exit = 1 - progressBetween(time, Math.max(start, end - fade), end);
  return clamp(Math.min(entrance, exit));
};

const stateFor = (states: FinanceSketchbookState[], id: FinanceSketchbookStateId): FinanceSketchbookState =>
  states.find((state) => state.id === id) || STATE_FALLBACKS[id];

const localPath = (path: string | undefined): string | undefined => {
  if (!path || !path.trim()) return undefined;
  const normalized = path.replaceAll("\\", "/").trim();
  if (/^(?:https?:|data:|blob:|file:|javascript:)/i.test(normalized) || normalized.startsWith("/") || /^[A-Za-z]:\//.test(normalized)) return undefined;
  const stripped = normalized.replace(/^public\//i, "").replace(/^(?:\.\/)+/, "");
  const parts = stripped.split("/");
  if (!stripped || parts.some((part) => !part || part === "." || part === "..")) return undefined;
  return stripped;
};

const Text: React.FC<{
  x: number;
  y: number;
  children: React.ReactNode;
  size?: number;
  fill?: string;
  anchor?: "start" | "middle" | "end";
  mono?: boolean;
  weight?: number;
  letterSpacing?: number;
}> = ({ x, y, children, size = 32, fill = COLORS.ink, anchor = "start", mono = false, weight = 400, letterSpacing }) => (
  <text
    x={x}
    y={y}
    fill={fill}
    textAnchor={anchor}
    fontFamily={mono ? "Space Mono, monospace" : size >= 52 ? "Archivo Black, Arial Black, sans-serif" : "Montserrat, Arial, sans-serif"}
    fontSize={size}
    fontWeight={mono || size >= 52 ? weight : Math.max(700, weight)}
    letterSpacing={letterSpacing}
    stroke="none"
  >
    {children}
  </text>
);

const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; color?: string; width?: number }> = ({ x1, y1, x2, y2, color = COLORS.ink, width = 12 }) => (
  <g>
    <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={width} strokeLinecap="round" />
    <path d={`M${x2 - 30} ${y2 - 24} L${x2} ${y2} L${x2 - 30} ${y2 + 24}`} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" />
  </g>
);

const Badge: React.FC<{ x: number; y: number; width: number; text: string; fill: string; rotate?: number }> = ({ x, y, width, text, fill, rotate = 0 }) => (
  <g transform={`rotate(${rotate} ${x + width / 2} ${y + 34})`}>
    <rect x={x} y={y} width={width} height={68} rx={18} fill={fill} stroke={COLORS.ink} strokeWidth={8} />
    <Text x={x + width / 2} y={y + 46} size={30} anchor="middle">{text}</Text>
  </g>
);

type WorldKind = "shop" | "home" | "market" | "office";

const World: React.FC<{ kind: WorldKind }> = ({ kind }) => {
  if (kind === "shop") {
    return (
      <g opacity={0.5} stroke={COLORS.ink} strokeWidth={8} strokeLinejoin="round">
        <rect x={90} y={690} width={1740} height={300} fill="#E9C3A0" />
        <path d="M110 755 H1810 M110 880 H1810" fill="none" />
        {Array.from({ length: 8 }, (_, index) => <rect key={`shop-item-${index}`} x={160 + index * 205} y={720 + (index % 2) * 116} width={105} height={70} rx={10} fill={index % 3 === 0 ? COLORS.yellow : index % 3 === 1 ? COLORS.red : COLORS.green} />)}
      </g>
    );
  }
  if (kind === "home") {
    return (
      <g opacity={0.48} stroke={COLORS.ink} strokeWidth={8} strokeLinejoin="round">
        <rect x={90} y={760} width={1740} height={230} fill="#D6C5AE" />
        <rect x={1370} y={190} width={340} height={250} rx={14} fill={COLORS.white} />
        <path d="M1540 190 V440 M1370 315 H1710" fill="none" />
        <path d="M210 920 Q290 810 370 920 V990 H210 Z" fill={COLORS.green} />
        <path d="M275 920 V680 M275 745 L205 690 M275 790 L350 710" fill="none" />
      </g>
    );
  }
  if (kind === "market") {
    return (
      <g opacity={0.46} stroke={COLORS.ink} strokeWidth={8} strokeLinejoin="round">
        <circle cx={1600} cy={220} r={78} fill={COLORS.yellow} />
        <path d="M90 780 Q410 650 730 780 T1370 780 T1830 780 V990 H90 Z" fill={COLORS.green} />
        <path d="M90 870 H1830" fill="none" />
        <path d="M1220 780 V520 H1400 V780 M1400 600 H1580 V780 M1580 700 H1780 V780" fill="#D9D4C8" />
      </g>
    );
  }
  return (
    <g opacity={0.45} stroke={COLORS.ink} strokeWidth={8} strokeLinejoin="round">
      <rect x={90} y={790} width={1740} height={200} fill="#D9D4C8" />
      <rect x={1320} y={170} width={410} height={230} rx={16} fill={COLORS.white} />
      <path d="M1380 230 H1670 M1380 285 H1600 M1380 340 H1640" fill="none" />
      <path d="M180 830 H680 V990 H180 Z" fill="#A9795E" />
      <rect x={230} y={770} width={180} height={60} rx={12} fill={COLORS.green} />
    </g>
  );
};

const Frame: React.FC<{ fill: string; number: string; eyebrow: string; world?: WorldKind; children: React.ReactNode }> = ({ fill, number, eyebrow, world, children }) => (
  <g>
    <rect x={64} y={52} width={1792} height={976} rx={42} fill={fill} stroke={COLORS.ink} strokeWidth={10} />
    {world ? <World kind={world} /> : null}
    <Text x={120} y={112} size={22} mono weight={700} letterSpacing={1.5}>{eyebrow}</Text>
    <Text x={1796} y={116} size={54} anchor="end">{number}</Text>
    {children}
  </g>
);

const PresenterPlate: React.FC<{
  assetPath: string;
  x: number;
  y: number;
  width: number;
  height?: number;
  opacity?: number;
  flip?: boolean;
}> = ({ assetPath, x, y, width, height = width * 1.777, opacity = 1, flip = false }) => (
  <image
    href={staticFile(assetPath)}
    x={flip ? x + width : x}
    y={y}
    width={width}
    height={height}
    opacity={opacity}
    preserveAspectRatio="xMidYMid meet"
    style={{ filter: "drop-shadow(0px 12px 8px rgba(17, 24, 32, 0.24))" }}
    transform={flip ? `translate(${2 * x + width} 0) scale(-1 1)` : undefined}
  />
);

const FundPackage: React.FC<{ x: number; y: number; scale?: number }> = ({ x, y, scale = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`} stroke={COLORS.ink} strokeWidth={11} strokeLinejoin="round">
    <path d="M-170 -130 L170 -130 L200 -95 L200 170 L-170 170 Z" fill={COLORS.yellow} />
    <path d="M170 -130 L205 -98 L205 166 L170 170 Z" fill={COLORS.red} />
    <path d="M-170 -130 L-135 -98 L205 -98" fill="none" />
    <rect x={-125} y={-30} width={250} height={86} rx={14} fill={COLORS.white} />
    <Text x={0} y={28} size={40} anchor="middle">S&amp;P 500</Text>
    <Text x={0} y={116} size={26} anchor="middle" mono weight={700}>INDEX FUND</Text>
  </g>
);

const Basket: React.FC<{ x: number; y: number; scale?: number }> = ({ x, y, scale = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`} stroke={COLORS.ink} strokeWidth={11} strokeLinejoin="round">
    <path d="M-260 -90 Q0 -250 260 -90" fill="none" strokeLinecap="round" />
    <path d="M-240 -75 L240 -75 L175 230 Q0 285 -175 230 Z" fill={COLORS.yellow} />
    <path d="M-195 -45 Q0 -135 195 -45" fill="none" stroke={COLORS.red} strokeWidth={18} strokeLinecap="round" />
    <Text x={0} y={70} size={44} anchor="middle">ONE BASKET</Text>
    <Text x={0} y={125} size={28} anchor="middle" mono weight={700}>500 HOLDINGS</Text>
  </g>
);

const SceneOne: React.FC<{ opacity: number; presenterAsset: string }> = ({ opacity, presenterAsset }) => (
  <g opacity={opacity}>
    <Frame fill={COLORS.blue} number="01" eyebrow="THE S&amp;P 500 INDEX FUND" world="shop">
      <Text x={150} y={270} size={92}>A GOOD</Text>
      <Text x={150} y={370} size={92} fill={COLORS.redDark}>PRODUCT.</Text>
      <PresenterPlate assetPath={presenterAsset} x={80} y={360} width={375} />
      <Arrow x1={470} y1={590} x2={700} y2={590} color={COLORS.redDark} />
      <FundPackage x={890} y={570} scale={1.12} />
      <Badge x={1225} y={310} width={260} text="CHEAP" fill={COLORS.yellow} rotate={-3} />
      <Badge x={1450} y={450} width={290} text="LIQUID" fill={COLORS.green} rotate={4} />
      <Badge x={1190} y={600} width={440} text="TAX-EFFICIENT" fill={COLORS.white} rotate={-2} />
      <Text x={1450} y={845} size={28} anchor="middle" mono weight={700}>THREE USEFUL QUALITIES</Text>
    </Frame>
  </g>
);

const SceneTwo: React.FC<{ opacity: number; presenterAsset: string }> = ({ opacity, presenterAsset }) => (
  <g opacity={opacity}>
    <Frame fill="#FFF0B9" number="02" eyebrow="ONE FAMILIAR BASKET" world="home">
      <Text x={150} y={250} size={92}>TWO</Text>
      <Text x={150} y={350} size={92} fill={COLORS.redDark}>JOBS.</Text>
      <Basket x={960} y={550} scale={0.95} />
      <PresenterPlate assetPath={presenterAsset} x={40} y={450} width={320} />
      <Arrow x1={680} y1={510} x2={420} y2={510} color={COLORS.blueDark} />
      <Arrow x1={1230} y1={510} x2={1510} y2={510} color={COLORS.redDark} />
      <Badge x={140} y={520} width={470} text="BROAD PROTECTION" fill={COLORS.blue} rotate={-3} />
      <Badge x={1320} y={520} width={430} text="EXCEPTIONAL UPSIDE" fill={COLORS.red} rotate={3} />
      <Text x={960} y={900} size={30} anchor="middle" mono weight={700}>ONE PRODUCT. TWO PROMISES.</Text>
    </Frame>
  </g>
);

const HoldingGrid: React.FC<{ x: number; y: number; opacity?: number; highlight?: string }> = ({ x, y, opacity = 1, highlight = COLORS.red }) => {
  const columns = 25;
  const rows = 20;
  const width = 720;
  const height = 440;
  const tile = 26;
  return (
    <g opacity={opacity}>
      <rect x={x - 28} y={y - 32} width={width + 56} height={height + 64} rx={30} fill={COLORS.white} stroke={COLORS.ink} strokeWidth={10} />
      {Array.from({ length: 500 }, (_, index) => {
        const column = index % columns;
        const row = Math.floor(index / columns);
        const isTopTen = index < 10;
        const cx = x + column * (width / columns) + tile / 2;
        const cy = y + row * (height / rows) + tile / 2;
        return isTopTen ? (
          <circle key={`holding-${index}`} cx={cx} cy={cy} r={16} fill={highlight} stroke={COLORS.ink} strokeWidth={4} />
        ) : (
          <circle key={`holding-${index}`} cx={cx} cy={cy} r={8} fill={COLORS.gray} stroke={COLORS.ink} strokeWidth={2} />
        );
      })}
    </g>
  );
};

const SceneThree: React.FC<{ opacity: number; source: FinanceSketchbookSourceCard; presenterAsset: string }> = ({ opacity, source, presenterAsset }) => (
  <g opacity={opacity}>
    <Frame fill="#F7D6D4" number="03" eyebrow="THE DIVERSIFICATION STORY" world="market">
      <Text x={150} y={255} size={82}>500 HOLDINGS.</Text>
      <Text x={150} y={350} size={54} fill={COLORS.redDark} mono weight={700}>BUT HOW MUCH IS WHERE?</Text>
      <HoldingGrid x={180} y={465} highlight={COLORS.red} />
      <PresenterPlate assetPath={presenterAsset} x={760} y={400} width={330} />
      <Text x={540} y={965} size={30} anchor="middle" mono weight={700}>TEN LARGE DOTS. MANY SMALL DOTS.</Text>
      <g>
        <rect x={1120} y={350} width={610} height={410} rx={30} fill={COLORS.yellow} stroke={COLORS.ink} strokeWidth={10} />
        <Text x={1425} y={515} size={122} anchor="middle">{source.display_text.split(" ")[0]}</Text>
        <Text x={1425} y={590} size={42} anchor="middle">OF INDEX WEIGHT</Text>
        <Text x={1425} y={660} size={24} anchor="middle" mono weight={700}>TEN LARGEST · MID-2025</Text>
        <title>{source.claim_text} {source.qualifier}</title>
      </g>
    </Frame>
  </g>
);

const WeatherCloud: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={11} strokeLinejoin="round">
    <path d="M-210 70 C-255 10 -215 -55 -145 -48 C-137 -128 -24 -150 14 -74 C70 -145 180 -108 165 -23 C242 -27 270 52 213 96 C170 129 67 112 0 110 C-90 130 -190 130 -210 70 Z" fill={COLORS.yellow} />
    <Text x={0} y={30} size={48} anchor="middle">SAME</Text>
    <Text x={0} y={86} size={48} anchor="middle">WEATHER</Text>
  </g>
);

const SceneFour: React.FC<{ opacity: number; presenterAsset: string }> = ({ opacity, presenterAsset }) => (
  <g opacity={opacity}>
    <Frame fill="#BDE6F5" number="04" eyebrow="THE SHARED WEATHER" world="market">
      <Text x={150} y={255} size={88}>LEADERS</Text>
      <Text x={150} y={350} size={88} fill={COLORS.redDark}>CAN MOVE</Text>
      <Text x={150} y={445} size={88}>TOGETHER.</Text>
      <WeatherCloud x={1410} y={410} />
      <PresenterPlate assetPath={presenterAsset} x={1450} y={390} width={330} />
      {Array.from({ length: 5 }, (_, index) => {
        const x = 310 + index * 125;
        const y = 720 - (index % 2) * 50;
        return (
          <g key={`leader-${index}`}>
            <circle cx={x} cy={y} r={42 + (index === 0 ? 12 : 0)} fill={index < 2 ? COLORS.red : COLORS.blueDark} stroke={COLORS.ink} strokeWidth={10} />
            <line x1={x + 55} y1={y - 20} x2={1310} y2={520 + index * 12} stroke={COLORS.ink} strokeWidth={8} strokeLinecap="round" />
          </g>
        );
      })}
      <Badge x={300} y={820} width={310} text="AI SPENDING" fill={COLORS.yellow} rotate={-4} />
      <Badge x={650} y={820} width={330} text="CLOUD CAPEX" fill={COLORS.white} rotate={3} />
      <Badge x={1030} y={820} width={390} text="SEMICONDUCTORS" fill={COLORS.red} rotate={-2} />
    </Frame>
  </g>
);

const SceneFive: React.FC<{ opacity: number; presenterAsset: string }> = ({ opacity, presenterAsset }) => (
  <g opacity={opacity}>
    <Frame fill="#D9F1D8" number="05" eyebrow="THE LONG TAIL" world="home">
      <Text x={150} y={255} size={86}>THE OTHER</Text>
      <Text x={150} y={365} size={128} fill={COLORS.greenDark}>490</Text>
      <Text x={150} y={455} size={60}>ARE STILL THERE.</Text>
      <HoldingGrid x={980} y={330} highlight={COLORS.blueDark} />
      <PresenterPlate assetPath={presenterAsset} x={730} y={420} width={300} />
      <rect x={190} y={620} width={660} height={170} rx={28} fill={COLORS.green} stroke={COLORS.ink} strokeWidth={10} />
      <Text x={520} y={700} size={48} anchor="middle">MOST OF THE</Text>
      <Text x={520} y={760} size={48} anchor="middle">REMAINING DOLLARS</Text>
      <Text x={970} y={900} size={28} anchor="middle" mono weight={700}>SIZE STILL MATTERS.</Text>
    </Frame>
  </g>
);

const Gate: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={11} strokeLinejoin="round">
    <rect x={-210} y={-150} width={420} height={500} rx={24} fill={COLORS.white} />
    <path d="M-155 -40 H155 M-155 80 H155 M-155 200 H155" stroke={COLORS.gray} />
    {["SIZE", "LIQUIDITY", "PROFITABILITY"].map((label, index) => (
      <g key={label}>
        <circle cx={-140} cy={index * 120 - 80} r={26} fill={COLORS.green} />
        <path d={`M${-152} ${index * 120 - 80} l10 12 l23 -30`} fill="none" stroke={COLORS.ink} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
        <Text x={-95} y={index * 120 - 70} size={32}>{label}</Text>
      </g>
    ))}
  </g>
);

const Scale: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={11} strokeLinecap="round" strokeLinejoin="round">
    <line x1={-300} y1={0} x2={300} y2={0} />
    <circle cx={0} cy={0} r={26} fill={COLORS.yellow} />
    <path d="M0 28 V190 L-80 260 H80 Z" fill={COLORS.red} />
    <path d="M-230 25 V120 M230 -25 V70" />
    <path d="M-330 120 Q-230 205 -130 120 L-155 225 Q-230 285 -305 225 Z" fill={COLORS.white} />
    <path d="M130 70 Q230 155 330 70 L305 175 Q230 235 155 175 Z" fill={COLORS.white} />
    <rect x={-300} y={150} width={125} height={36} rx={5} fill={COLORS.gray} />
    <rect x={-275} y={108} width={80} height={36} rx={5} fill={COLORS.gray} />
    <rect x={205} y={70} width={42} height={36} rx={5} fill={COLORS.blueDark} />
    <rect x={250} y={30} width={42} height={36} rx={5} fill={COLORS.blueDark} />
    <rect x={295} y={-10} width={42} height={36} rx={5} fill={COLORS.blueDark} />
  </g>
);

const SceneSix: React.FC<{ opacity: number; presenterAsset: string }> = ({ opacity, presenterAsset }) => (
  <g opacity={opacity}>
    <Frame fill={COLORS.lilac} number="06" eyebrow="THE LAST DISTINCTION" world="office">
      <Text x={150} y={230} size={72}>ADMISSION</Text>
      <Text x={150} y={320} size={72} fill={COLORS.redDark}>IS NOT</Text>
      <Text x={150} y={410} size={72}>WEIGHTING.</Text>
      <Gate x={420} y={650} />
      <Arrow x1={650} y1={620} x2={910} y2={620} color={COLORS.greenDark} />
      <PresenterPlate assetPath={presenterAsset} x={620} y={390} width={340} />
      <Scale x={1320} y={530} />
      <Text x={1090} y={850} size={42} anchor="middle">ELIGIBLE</Text>
      <Text x={1570} y={850} size={32} anchor="middle" fill={COLORS.blueDark}>BIGGER = MORE WEIGHT</Text>
      <Text x={1310} y={940} size={38} anchor="middle" mono weight={700}>A GOOD INDEX IS NOT A BAG OF RANDOM JUNK.</Text>
    </Frame>
  </g>
);

export const defaultFinanceSketchbookProps: FinanceSketchbookProofProps = {
  schema_version: "finance_sketchbook_proof.v1",
  proof_id: "finance-sketchbook-proof-v1",
  duration_s: 60.732,
  source_start_s: 410.26,
  source_end_s: 470.992,
  source_word_start: 1025,
  source_word_end: 1188,
  delivery_fps: 24,
  paper_motion_fps: 12,
  authoring_profile: { width: 1920, height: 1080, fps: 24 },
  render_profile: { width: 1920, height: 1080, fps: 24, label: "authoring-1080p" },
  canonical_audio: { path: "", start_s: 410.26, volume: 1 },
  presenter_asset: {
    asset_id: "finance-host-presenter-plate-v1",
    path: "assets/finance-host-presenter-plate-v1.png",
    sha256: "16c94909dcdcd2e6ce369467c3971ce949dfbe5f5a13b7a32b6baea2649009c8",
    render_state: "draft",
  },
  states: Object.values(STATE_FALLBACKS),
  concentration_source: {
    claim_id: "sp500-top-ten-concentration",
    claim_text: "The ten largest S&amp;P 500 companies represented almost 40% of the index by mid-2025, a concentration level not seen since the mid-1960s.",
    display_text: "≈40% of index weight",
    as_of: "2025-06-30",
    source_locator: "sp500-top-ten-concentration · PDF p. 4",
    source_location: "PDF page 4, highlights and top-ten concentration chart",
    qualifier: "Concentration alone does not prove overvaluation or predict a market decline.",
  },
};

export const calculateFinanceSketchbookMetadata: CalculateMetadataFunction<FinanceSketchbookProofProps> = ({ props }) => {
  const profile = props.render_profile || props.authoring_profile;
  const fps = Math.max(1, Math.round(finite(profile.fps, 24)));
  return {
    durationInFrames: Math.max(1, Math.round(props.duration_s * fps)),
    width: Math.max(1, Math.round(finite(profile.width, VIEWBOX.width))),
    height: Math.max(1, Math.round(finite(profile.height, VIEWBOX.height))),
    fps,
  };
};

export const FinanceSketchbookProof: React.FC<FinanceSketchbookProofProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const time = steppedTime(frame, fps);
  const s1 = stateFor(props.states, "basket-product-qualities");
  const s2 = stateFor(props.states, "two-jobs");
  const s3 = stateFor(props.states, "concentration");
  const s4 = stateFor(props.states, "shared-exposure");
  const s5 = stateFor(props.states, "long-tail");
  const s6 = stateFor(props.states, "admission-versus-weighting");
  const audio = localPath(props.canonical_audio.path);
  const presenterAsset = localPath(props.presenter_asset?.path) || "assets/finance-host-presenter-plate-v1.png";
  const audioStart = Math.max(0, Math.round(props.canonical_audio.start_s * fps));

  return (
    <div style={{ width: "100%", height: "100%", overflow: "hidden", background: COLORS.paper }}>
      <svg viewBox={`0 0 ${VIEWBOX.width} ${VIEWBOX.height}`} width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
        <rect width={VIEWBOX.width} height={VIEWBOX.height} fill={COLORS.paper} />
        <SceneOne opacity={windowOpacity(time, s1.relative_start_s, s2.relative_start_s)} presenterAsset={presenterAsset} />
        <SceneTwo opacity={windowOpacity(time, s2.relative_start_s, s3.relative_start_s)} presenterAsset={presenterAsset} />
        <SceneThree opacity={windowOpacity(time, s3.relative_start_s, s4.relative_start_s)} source={props.concentration_source} presenterAsset={presenterAsset} />
        <SceneFour opacity={windowOpacity(time, s4.relative_start_s, s5.relative_start_s)} presenterAsset={presenterAsset} />
        <SceneFive opacity={windowOpacity(time, s5.relative_start_s, s6.relative_start_s)} presenterAsset={presenterAsset} />
        <SceneSix opacity={windowOpacity(time, s6.relative_start_s, props.duration_s)} presenterAsset={presenterAsset} />
      </svg>
      {audio ? <Audio src={staticFile(audio)} startFrom={audioStart} volume={props.canonical_audio.volume} /> : null}
    </div>
  );
};
