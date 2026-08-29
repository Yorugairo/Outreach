import React from "react";
import {
  Audio,
  type CalculateMetadataFunction,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {
  Finance2DStickProofProps,
  Finance2DStickSourceCard,
  Finance2DStickState,
  Finance2DStickStateId,
} from "./types";

const COLORS = {
  paper: "#FFFFFF",
  ink: "#171717",
  skin: "#F1C4A8",
  skinShadow: "#D99573",
  hair: "#5C3928",
  shirt: "#4E92C8",
  shirtDark: "#2D6188",
  green: "#77B87A",
  greenDark: "#2A7048",
  yellow: "#F4D66D",
  yellowDark: "#B88C23",
  coral: "#E86B62",
  coralDark: "#A94440",
  blue: "#B9DEF0",
  blueDark: "#477A98",
  gray: "#DDE1E3",
  grayDark: "#778087",
  cream: "#FFF4D8",
};

const VIEWBOX = { width: 1920, height: 1080 };

const STATE_FALLBACKS: Record<Finance2DStickStateId, Finance2DStickState> = {
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
const smooth = (value: number): number => {
  const t = clamp(value);
  return t * t * (3 - 2 * t);
};
const reveal = (progress: number, start: number, duration = 0.18): number =>
  smooth((progress - start) / Math.max(0.01, duration));
const stateFor = (states: Finance2DStickState[], id: Finance2DStickStateId): Finance2DStickState =>
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
  weight?: number;
  family?: "friendly" | "number";
  letterSpacing?: number;
}> = ({ x, y, children, size = 34, fill = COLORS.ink, anchor = "start", weight = 700, family = "friendly", letterSpacing }) => (
  <text
    x={x}
    y={y}
    fill={fill}
    textAnchor={anchor}
    fontFamily={family === "number" ? "Arial, sans-serif" : "Trebuchet MS, Arial, sans-serif"}
    fontSize={size}
    fontWeight={weight}
    letterSpacing={letterSpacing}
    stroke="none"
  >
    {children}
  </text>
);

const Line: React.FC<{ d: string; color?: string; width?: number; dash?: string }> = ({ d, color = COLORS.ink, width = 9, dash }) => (
  <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} />
);

const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; color?: string; width?: number }> = ({ x1, y1, x2, y2, color = COLORS.ink, width = 10 }) => {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const size = 23;
  const p1 = `${x2 - size * Math.cos(angle - Math.PI / 6)},${y2 - size * Math.sin(angle - Math.PI / 6)}`;
  const p2 = `${x2 - size * Math.cos(angle + Math.PI / 6)},${y2 - size * Math.sin(angle + Math.PI / 6)}`;
  return (
    <g>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={width} strokeLinecap="round" />
      <path d={`M${p1} L${x2},${y2} L${p2}`} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" />
    </g>
  );
};

const Label: React.FC<{ x: number; y: number; width: number; text: string; fill: string; rotate?: number; size?: number }> = ({ x, y, width, text, fill, rotate = 0, size = 30 }) => (
  <g transform={`rotate(${rotate} ${x + width / 2} ${y + 29})`}>
    <rect x={x} y={y} width={width} height={58} rx={12} fill={fill} stroke={COLORS.ink} strokeWidth={7} />
    <Text x={x + width / 2} y={y + 39} size={size} anchor="middle">{text}</Text>
  </g>
);

type Expression = "smile" | "curious" | "skeptical" | "surprised" | "thinking" | "confident";
type Pose = "point" | "shrug" | "think" | "open" | "cheer" | "hands";

const StickPerson: React.FC<{ x: number; y: number; scale?: number; expression?: Expression; pose?: Pose; flip?: boolean }> = ({ x, y, scale = 1, expression = "smile", pose = "hands", flip = false }) => {
  const mouth = {
    smile: <path d="M-30 -194 Q0 -165 30 -194" />,
    curious: <ellipse cx="0" cy={-180} rx="20" ry="27" />,
    skeptical: <path d="M-28 -183 H28" />,
    surprised: <ellipse cx="0" cy={-180} rx="18" ry="30" />,
    thinking: <path d="M-24 -182 Q0 -171 24 -182" />,
    confident: <path d="M-33 -192 Q0 -160 34 -192" />,
  }[expression];
  const brows = expression === "skeptical"
    ? <><Line d="M-65 -255 L-14 -267" width={10} /><Line d="M15 -260 L67 -250" width={10} /></>
    : expression === "surprised"
      ? <><Line d="M-65 -263 Q-40 -282 -15 -263" width={9} /><Line d="M15 -263 Q40 -282 65 -263" width={9} /></>
      : <><Line d="M-64 -260 Q-40 -273 -16 -260" width={9} /><Line d="M16 -260 Q40 -273 64 -260" width={9} /></>;
  const eyes = expression === "thinking"
    ? <><ellipse cx={-42} cy={-225} rx={23} ry={28} fill={COLORS.paper} /><ellipse cx={42} cy={-225} rx={23} ry={28} fill={COLORS.paper} /><circle cx={-34} cy={-225} r={8} /><circle cx={50} cy={-225} r={8} /></>
    : expression === "surprised"
      ? <><ellipse cx={-42} cy={-225} rx={25} ry={32} fill={COLORS.paper} /><ellipse cx={42} cy={-225} rx={25} ry={32} fill={COLORS.paper} /><circle cx={-42} cy={-225} r={10} /><circle cx={42} cy={-225} r={10} /></>
      : <><ellipse cx={-42} cy={-225} rx={23} ry={28} fill={COLORS.paper} /><ellipse cx={42} cy={-225} rx={23} ry={28} fill={COLORS.paper} /><circle cx={-35} cy={-224} r={8} /><circle cx={49} cy={-224} r={8} /></>;
  const armSet = {
    point: <><Line d="M-78 -35 Q-165 -40 -230 -108" /><Line d="M78 -35 Q155 -35 240 -145" /><circle cx={240} cy={-145} r={17} fill={COLORS.skin} /></>,
    shrug: <><Line d="M-78 -35 Q-165 -10 -208 -92" /><Line d="M78 -35 Q165 -10 208 -92" /><circle cx={-208} cy={-92} r={17} fill={COLORS.skin} /><circle cx={208} cy={-92} r={17} fill={COLORS.skin} /></>,
    think: <><Line d="M-78 -35 Q-165 30 -152 92" /><Line d="M78 -35 Q130 -15 120 -100 Q112 -143 54 -164" /><circle cx={54} cy={-164} r={17} fill={COLORS.skin} /></>,
    open: <><Line d="M-78 -35 Q-190 -20 -255 -90" /><Line d="M78 -35 Q190 -20 255 -90" /><circle cx={-255} cy={-90} r={17} fill={COLORS.skin} /><circle cx={255} cy={-90} r={17} fill={COLORS.skin} /></>,
    cheer: <><Line d="M-78 -35 Q-150 -110 -165 -220" /><Line d="M78 -35 Q170 -100 175 -250" /><circle cx={-165} cy={-220} r={17} fill={COLORS.skin} /><circle cx={175} cy={-250} r={17} fill={COLORS.skin} /></>,
    hands: <><Line d="M-78 -35 Q-130 40 -98 112" /><Line d="M78 -35 Q130 40 98 112" /><circle cx={-98} cy={112} r={17} fill={COLORS.skin} /><circle cx={98} cy={112} r={17} fill={COLORS.skin} /></>,
  }[pose];
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -scale : scale} ${scale})`} stroke={COLORS.ink} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx={0} cy={-220} rx={112} ry={125} fill={COLORS.skin} />
      <path d="M-105 -250 Q-118 -363 0 -365 Q119 -360 105 -245 Q73 -285 42 -309 Q-18 -282 -105 -250 Z" fill={COLORS.hair} />
      {brows}
      {eyes}
      <path d="M0 -212 Q-6 -203 0 -195" />
      {mouth}
      <path d="M-38 -100 H38" />
      <path d="M-88 -102 Q-97 -45 -82 82 L82 82 Q97 -45 88 -102 Z" fill={COLORS.shirt} />
      {armSet}
      <Line d="M-42 82 L-62 285" width={11} />
      <Line d="M42 82 L62 285" width={11} />
      <path d="M-80 285 Q-48 266 -18 285" fill={COLORS.grayDark} />
      <path d="M18 285 Q48 266 80 285" fill={COLORS.grayDark} />
    </g>
  );
};

const SceneHeader: React.FC<{ eyebrow: string; title: string; subtitle?: string }> = ({ eyebrow, title, subtitle }) => (
  <g>
    <Text x={112} y={94} size={22} weight={700} letterSpacing={2}>{eyebrow}</Text>
    <Text x={112} y={190} size={76} weight={800}>{title}</Text>
    {subtitle ? <Text x={112} y={245} size={32} weight={700} fill={COLORS.grayDark}>{subtitle}</Text> : null}
  </g>
);

const Ground: React.FC = () => <Line d="M95 930 H1825" color="#B8BEC2" width={5} />;

const IndexBasket: React.FC<{ x: number; y: number; scale?: number; progress?: number }> = ({ x, y, scale = 1, progress = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`} stroke={COLORS.ink} strokeWidth={9} strokeLinejoin="round">
    <path d="M-180 -105 Q0 -230 180 -105" fill="none" />
    <path d="M-170 -90 H170 L124 185 Q0 245 -124 185 Z" fill={COLORS.yellow} />
    <path d="M-135 -65 Q0 -138 135 -65" fill="none" stroke={COLORS.coral} strokeWidth={18} />
    <rect x={-112} y={-18} width={224} height={78} rx={12} fill={COLORS.paper} />
    <Text x={0} y={34} size={40} anchor="middle">S&amp;P 500</Text>
    {Array.from({ length: 12 }, (_, index) => <circle key={index} cx={-88 + (index % 4) * 58} cy={88 + Math.floor(index / 4) * 42} r={index < 3 ? 15 : 9} fill={index < 3 ? COLORS.green : COLORS.blueDark} opacity={reveal(progress, 0.1 + index * 0.03)} />)}
  </g>
);

const Shield: React.FC<{ x: number; y: number; fill?: string }> = ({ x, y, fill = COLORS.blue }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={9} strokeLinejoin="round">
    <path d="M0 -115 L110 -72 V28 Q92 120 0 170 Q-92 120 -110 28 V-72 Z" fill={fill} />
    <path d="M-45 8 L-12 42 L57 -39" fill="none" stroke={COLORS.greenDark} strokeWidth={18} strokeLinecap="round" />
  </g>
);

const GrowthArrow: React.FC<{ x: number; y: number; color?: string }> = ({ x, y, color = COLORS.greenDark }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={9} strokeLinejoin="round">
    <path d="M-120 95 L-42 15 L10 47 L112 -76" fill="none" stroke={color} strokeWidth={26} strokeLinecap="round" />
    <path d="M72 -78 H124 V-27" fill="none" stroke={color} strokeWidth={26} strokeLinecap="round" />
  </g>
);

const DotGrid: React.FC<{ x: number; y: number; progress: number }> = ({ x, y, progress }) => (
  <g>
    <rect x={x - 38} y={y - 38} width={770} height={440} rx={18} fill={COLORS.cream} stroke={COLORS.ink} strokeWidth={9} />
    {Array.from({ length: 100 }, (_, index) => {
      const col = index % 10;
      const row = Math.floor(index / 10);
      const big = index < 10;
      return <circle key={index} cx={x + col * 70} cy={y + row * 38} r={big ? 22 : 10} fill={big ? COLORS.coral : COLORS.gray} stroke={COLORS.ink} strokeWidth={big ? 6 : 3} opacity={reveal(progress, index < 10 ? 0.18 : 0.3 + (index % 10) * 0.02, 0.12)} />;
    })}
    <Text x={x + 350} y={y + 435} size={28} anchor="middle" family="number">500 COMPANIES IN THE BASKET</Text>
  </g>
);

const WeatherCloud: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={9} strokeLinejoin="round">
    <path d="M-160 35 Q-185 -55 -98 -66 Q-64 -145 15 -90 Q74 -142 127 -83 Q217 -85 203 8 Q178 65 100 58 H-102 Q-147 63 -160 35 Z" fill={COLORS.blue} />
    <Text x={0} y={38} size={29} anchor="middle">SHARED WEATHER</Text>
  </g>
);

const CompanyToken: React.FC<{ x: number; y: number; scale?: number; color?: string }> = ({ x, y, scale = 1, color = COLORS.green }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`} stroke={COLORS.ink} strokeWidth={8} strokeLinejoin="round">
    <rect x={-70} y={-55} width={140} height={110} rx={16} fill={color} />
    <path d="M-36 54 V-5 Q0 -45 36 -5 V54" fill={COLORS.paper} />
    <circle cx={0} cy={-6} r={14} fill={color} />
  </g>
);

const MoneyStack: React.FC<{ x: number; y: number; scale?: number }> = ({ x, y, scale = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`} stroke={COLORS.ink} strokeWidth={9} strokeLinejoin="round">
    <path d="M-180 125 L-155 -45 L160 -90 L185 80 Z" fill={COLORS.green} />
    <path d="M-160 65 L160 28 M-166 0 L154 -38 M-153 -62 L168 -99" fill="none" stroke={COLORS.greenDark} strokeWidth={12} />
    <Text x={0} y={40} size={64} anchor="middle" family="number">$</Text>
  </g>
);

const CheckGate: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={9} strokeLinejoin="round">
    <rect x={-220} y={-195} width={440} height={420} rx={18} fill={COLORS.paper} />
    <Text x={0} y={-135} size={32} anchor="middle">ENTRY RULES</Text>
    {["SIZE", "LIQUIDITY", "PROFITABILITY"].map((label, index) => (
      <g key={label} transform={`translate(0 ${-55 + index * 105})`}>
        <circle cx={-164} cy={0} r={25} fill={COLORS.green} />
        <path d="M-176 0 L-166 12 L-145 -17" fill="none" stroke={COLORS.ink} strokeWidth={7} />
        <Text x={-116} y={10} size={30}>{label}</Text>
      </g>
    ))}
  </g>
);

const WeightScale: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`} stroke={COLORS.ink} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round">
    <line x1={-270} y1={0} x2={270} y2={0} />
    <circle cx={0} cy={0} r={25} fill={COLORS.yellow} />
    <line x1={0} y1={25} x2={0} y2={180} />
    <path d="M-90 220 H90 L0 180 Z" fill={COLORS.coral} />
    <path d="M-215 30 V130 M215 -30 V70" />
    <path d="M-320 130 Q-215 230 -110 130 L-135 250 Q-215 305 -295 250 Z" fill={COLORS.paper} />
    <path d="M110 70 Q215 170 320 70 L295 190 Q215 245 135 190 Z" fill={COLORS.paper} />
    <rect x={-270} y={150} width={125} height={34} rx={5} fill={COLORS.gray} />
    <rect x={-238} y={112} width={85} height={34} rx={5} fill={COLORS.gray} />
    <rect x={190} y={48} width={42} height={34} rx={5} fill={COLORS.greenDark} />
    <rect x={240} y={10} width={42} height={34} rx={5} fill={COLORS.greenDark} />
    <rect x={290} y={-28} width={42} height={34} rx={5} fill={COLORS.greenDark} />
  </g>
);

const SceneOne: React.FC<{ progress: number }> = ({ progress }) => (
  <g>
    <SceneHeader eyebrow="THE OTHER ELEVATOR" title="A GOOD PRODUCT." subtitle="The S&amp;P 500 index fund" />
    <g opacity={reveal(progress, 0.14)}>
      <StickPerson x={360} y={850} scale={1.02} expression="curious" pose="point" />
      <Arrow x1={510} y1={730} x2={705} y2={625} color={COLORS.coralDark} />
    </g>
    <g opacity={reveal(progress, 0.28)}>
      <IndexBasket x={970} y={610} scale={1.18} progress={progress} />
    </g>
    <g opacity={reveal(progress, 0.45)}>
      <Label x={1310} y={370} width={220} text="CHEAP" fill={COLORS.yellow} rotate={-3} />
      <Label x={1450} y={490} width={240} text="LIQUID" fill={COLORS.blue} rotate={3} />
      <Label x={1280} y={610} width={410} text="TAX-EFFICIENT" fill={COLORS.green} rotate={-2} size={28} />
      <Text x={1485} y={755} size={25} anchor="middle" fill={COLORS.grayDark}>THREE USEFUL QUALITIES</Text>
    </g>
    <Ground />
  </g>
);

const SceneTwo: React.FC<{ progress: number }> = ({ progress }) => (
  <g>
    <SceneHeader eyebrow="THE SUBTLE PROBLEM" title="TWO JOBS." subtitle="One fund can be asked to do both" />
    <g opacity={reveal(progress, 0.16)}>
      <StickPerson x={960} y={860} scale={1.05} expression="skeptical" pose="shrug" />
    </g>
    <g opacity={reveal(progress, 0.3)}>
      <Shield x={450} y={560} />
      <Text x={450} y={770} size={43} anchor="middle">PROTECT</Text>
      <Text x={450} y={812} size={26} anchor="middle" fill={COLORS.grayDark}>broad diversification</Text>
      <GrowthArrow x={1450} y={565} />
      <Text x={1450} y={770} size={43} anchor="middle">CAPTURE UPSIDE</Text>
      <Text x={1450} y={812} size={26} anchor="middle" fill={COLORS.grayDark}>own the leaders</Text>
    </g>
    <g opacity={reveal(progress, 0.58)}>
      <circle cx={960} cy={390} r={62} fill={COLORS.coral} stroke={COLORS.ink} strokeWidth={9} />
      <Line d="M920 350 L1000 430 M1000 350 L920 430" color={COLORS.paper} width={15} />
      <Text x={960} y={280} size={32} anchor="middle">THE INDEX CAN FAIL BOTH JOBS AT ONCE.</Text>
    </g>
    <Ground />
  </g>
);

const SceneThree: React.FC<{ progress: number; source: Finance2DStickSourceCard }> = ({ progress, source }) => (
  <g>
    <SceneHeader eyebrow="THE CONCENTRATION" title="500 HOLDINGS." subtitle="But how much is actually where?" />
    <g opacity={reveal(progress, 0.12)}>
      <StickPerson x={330} y={860} scale={1.03} expression="surprised" pose="open" />
    </g>
    <g opacity={reveal(progress, 0.28)}>
      <DotGrid x={720} y={390} progress={progress} />
      <Arrow x1={1100} y1={815} x2={1390} y2={870} color={COLORS.coralDark} />
      <rect x={1280} y={800} width={520} height={145} rx={18} fill={COLORS.yellow} stroke={COLORS.ink} strokeWidth={9} />
      <Text x={1540} y={870} size={46} anchor="middle" family="number">{source.display_text}</Text>
      <Text x={1540} y={912} size={22} anchor="middle" fill={COLORS.grayDark}>MID-2025 · SOURCE-BOUND</Text>
      <title>{source.claim_text} {source.qualifier}</title>
    </g>
    <Ground />
  </g>
);

const SceneFour: React.FC<{ progress: number }> = ({ progress }) => (
  <g>
    <SceneHeader eyebrow="THE SHARED WEATHER" title="LEADERS MOVE TOGETHER." subtitle="Different companies. Similar exposure." />
    <g opacity={reveal(progress, 0.16)}>
      <StickPerson x={410} y={860} scale={1.02} expression="skeptical" pose="think" />
      <WeatherCloud x={1060} y={390} />
    </g>
    <g opacity={reveal(progress, 0.34)}>
      {[{ x: 700, y: 720, label: "AI SPENDING", fill: COLORS.yellow }, { x: 1000, y: 780, label: "CLOUD CAPEX", fill: COLORS.blue }, { x: 1300, y: 720, label: "CHIP SUPPLY", fill: COLORS.green }, { x: 1600, y: 780, label: "PREMIUM VALUATIONS", fill: COLORS.cream }].map((item) => (
        <g key={item.label}>
          <CompanyToken x={item.x} y={item.y} color={item.fill} />
          <Arrow x1={item.x} y1={item.y - 90} x2={1060} y2={495} color={COLORS.blueDark} width={7} />
          <Label x={item.x - 115} y={item.y + 90} width={230} text={item.label} fill={item.fill} size={20} />
        </g>
      ))}
    </g>
    <Text x={1080} y={1000} size={34} anchor="middle">THE BASKET LOOKS DIVERSIFIED. THE WEATHER ISN'T.</Text>
    <Ground />
  </g>
);

const SceneFive: React.FC<{ progress: number }> = ({ progress }) => (
  <g>
    <SceneHeader eyebrow="THE LONG TAIL" title="THE OTHER 490." subtitle="Still there. Still consuming most of the remaining dollar." />
    <g opacity={reveal(progress, 0.12)}>
      <StickPerson x={360} y={860} scale={1.03} expression="thinking" pose="think" />
    </g>
    <g opacity={reveal(progress, 0.27)}>
      <Text x={820} y={370} size={32} anchor="middle">THE LEADERS</Text>
      {Array.from({ length: 10 }, (_, index) => <circle key={index} cx={680 + (index % 5) * 72} cy={470 + Math.floor(index / 5) * 72} r={25} fill={COLORS.coral} stroke={COLORS.ink} strokeWidth={7} />)}
      <Arrow x1={1050} y1={520} x2={1250} y2={610} color={COLORS.greenDark} />
      <Text x={1450} y={370} size={32} anchor="middle">THE OTHER 490</Text>
      {Array.from({ length: 40 }, (_, index) => <circle key={index} cx={1210 + (index % 10) * 48} cy={430 + Math.floor(index / 10) * 48} r={index < 10 ? 11 : 8} fill={COLORS.gray} stroke={COLORS.ink} strokeWidth={3} />)}
      <MoneyStack x={1510} y={800} scale={1.0} />
    </g>
    <g opacity={reveal(progress, 0.58)}>
      <Label x={1090} y={915} width={690} text="MOST OF THE REMAINING DOLLAR" fill={COLORS.green} size={27} />
    </g>
    <Ground />
  </g>
);

const SceneSix: React.FC<{ progress: number }> = ({ progress }) => (
  <g>
    <SceneHeader eyebrow="THE LAST DISTINCTION" title="ADMISSION ≠ WEIGHTING." subtitle="A good index is not a bag of random junk." />
    <g opacity={reveal(progress, 0.12)}>
      <StickPerson x={340} y={860} scale={1.04} expression="confident" pose="point" />
      <Arrow x1={505} y1={700} x2={680} y2={600} color={COLORS.greenDark} />
    </g>
    <g opacity={reveal(progress, 0.28)}>
      <CheckGate x={920} y={590} />
      <Arrow x1={1160} y1={600} x2={1300} y2={600} color={COLORS.coralDark} />
      <WeightScale x={1570} y={575} />
    </g>
    <g opacity={reveal(progress, 0.56)}>
      <Text x={920} y={880} size={30} anchor="middle">ELIGIBLE</Text>
      <Text x={1570} y={880} size={30} anchor="middle">BIGGER = MORE WEIGHT</Text>
      <Label x={625} y={930} width={860} text="SIZE · LIQUIDITY · PROFITABILITY" fill={COLORS.yellow} size={30} />
    </g>
    <Ground />
  </g>
);

export const defaultFinance2DStickProps: Finance2DStickProofProps = {
  schema_version: "finance_2d_stick_proof.v1",
  proof_id: "finance-2d-stick-proof-v1",
  duration_s: 60.732,
  source_start_s: 410.26,
  source_end_s: 470.992,
  source_word_start: 1025,
  source_word_end: 1188,
  delivery_fps: 24,
  authoring_profile: { width: 1920, height: 1080, fps: 24 },
  render_profile: { width: 1920, height: 1080, fps: 24, label: "authoring-1080p" },
  canonical_audio: { path: "", start_s: 410.26, volume: 1 },
  states: Object.values(STATE_FALLBACKS),
  concentration_source: {
    claim_id: "sp500-top-ten-concentration",
    claim_text: "The ten largest S&P 500 companies represented almost 40% of the index by mid-2025, a concentration level not seen since the mid-1960s.",
    display_text: "≈40% of index weight",
    as_of: "2025-06-30",
    source_locator: "sp500-top-ten-concentration · PDF p. 4",
    source_location: "PDF page 4, highlights and top-ten concentration chart",
    qualifier: "Concentration alone does not prove overvaluation or predict a market decline.",
  },
};

export const calculateFinance2DStickMetadata: CalculateMetadataFunction<Finance2DStickProofProps> = ({ props }) => {
  const profile = props.render_profile || props.authoring_profile;
  const fps = Math.max(1, Math.round(finite(profile.fps, 24)));
  return {
    durationInFrames: Math.max(1, Math.round(props.duration_s * fps)),
    width: Math.max(1, Math.round(finite(profile.width, VIEWBOX.width))),
    height: Math.max(1, Math.round(finite(profile.height, VIEWBOX.height))),
    fps,
  };
};

export const Finance2DStickProof: React.FC<Finance2DStickProofProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const time = frame / fps;
  const states = props.states;
  const current = states.find((state) => time >= state.relative_start_s && time < state.relative_end_s) || states[states.length - 1] || STATE_FALLBACKS["admission-versus-weighting"];
  const progress = clamp((time - current.relative_start_s) / Math.max(0.001, current.relative_end_s - current.relative_start_s));
  const audio = localPath(props.canonical_audio.path);
  const audioStart = Math.max(0, Math.round(props.canonical_audio.start_s * fps));

  return (
    <div style={{ width: "100%", height: "100%", overflow: "hidden", background: COLORS.paper }}>
      <svg viewBox={`0 0 ${VIEWBOX.width} ${VIEWBOX.height}`} width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
        <rect width={VIEWBOX.width} height={VIEWBOX.height} fill={COLORS.paper} />
        {current.id === "basket-product-qualities" ? <SceneOne progress={progress} /> : null}
        {current.id === "two-jobs" ? <SceneTwo progress={progress} /> : null}
        {current.id === "concentration" ? <SceneThree progress={progress} source={props.concentration_source} /> : null}
        {current.id === "shared-exposure" ? <SceneFour progress={progress} /> : null}
        {current.id === "long-tail" ? <SceneFive progress={progress} /> : null}
        {current.id === "admission-versus-weighting" ? <SceneSix progress={progress} /> : null}
      </svg>
      {audio ? <Audio src={staticFile(audio)} startFrom={audioStart} volume={props.canonical_audio.volume} /> : null}
    </div>
  );
};
