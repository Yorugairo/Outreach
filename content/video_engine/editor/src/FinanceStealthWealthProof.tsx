import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {
  FinanceStealthWealthAsset,
  FinanceStealthWealthBeat,
  FinanceStealthWealthClaim,
  FinanceStealthWealthProofProps,
} from "./types";

const DESIGN = { width: 1920, height: 1080 } as const;
const COLORS = {
  charcoal: "#111417",
  charcoalSoft: "#1A1E21",
  ink: "#F2EEE5",
  muted: "#A6AAA7",
  amber: "#D6A56B",
  amberSoft: "#E7C08C",
  emerald: "#6EC9A4",
  emeraldDeep: "#16483C",
  red: "#D77F73",
  slate: "#9CB8C4",
  glass: "rgba(18, 22, 24, 0.68)",
  glassLight: "rgba(247, 244, 236, 0.12)",
} as const;

const finite = (value: number, fallback: number): number =>
  Number.isFinite(value) ? value : fallback;

const localAsset = (asset: FinanceStealthWealthAsset | undefined, fallback: string): string =>
  staticFile(asset?.path || fallback);

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value));

const fade = (time: number, start: number, end: number, fadeIn = 0.8, fadeOut = 0.8): number => {
  const enter = clamp01((time - start) / fadeIn);
  const exit = clamp01((end - time) / fadeOut);
  return enter * exit;
};

const beatOpacity = (time: number, beat: FinanceStealthWealthBeat): number =>
  fade(time, beat.start_s, beat.end_s);

const claim = (claims: FinanceStealthWealthClaim[], id: string): FinanceStealthWealthClaim =>
  claims.find((item) => item.claim_id === id) || {
    claim_id: id,
    display_text: "",
    claim_text: "",
    source_locator: "",
    citation: "",
    kind: "mechanism",
  };

const Text: React.FC<{
  x: number;
  y: number;
  children: React.ReactNode;
  size?: number;
  fill?: string;
  anchor?: "start" | "middle" | "end";
  weight?: number;
  family?: "sans" | "serif" | "mono";
  letterSpacing?: number;
  opacity?: number;
}> = ({
  x,
  y,
  children,
  size = 30,
  fill = COLORS.ink,
  anchor = "start",
  weight = 500,
  family = "sans",
  letterSpacing,
  opacity = 1,
}) => (
  <text
    x={x}
    y={y}
    fill={fill}
    textAnchor={anchor}
    opacity={opacity}
    fontFamily={family === "serif" ? "Georgia, Times New Roman, serif" : family === "mono" ? "Consolas, monospace" : "Arial, Helvetica, sans-serif"}
    fontSize={size}
    fontWeight={weight}
    letterSpacing={letterSpacing}
  >
    {children}
  </text>
);

const GlassCard: React.FC<{
  x: number;
  y: number;
  width: number;
  height: number;
  eyebrow?: string;
  accent?: string;
  children: React.ReactNode;
  opacity?: number;
}> = ({ x, y, width, height, eyebrow, accent = COLORS.emerald, children, opacity = 1 }) => (
  <g opacity={opacity}>
    <rect x={x} y={y} width={width} height={height} rx={30} fill={COLORS.glass} stroke="rgba(242,238,229,0.25)" strokeWidth={2} />
    <rect x={x + 2} y={y + 2} width={width - 4} height={5} rx={3} fill={accent} opacity={0.88} />
    <rect x={x + 28} y={y + 26} width={7} height={height - 52} rx={4} fill={accent} opacity={0.9} />
    {eyebrow ? <Text x={x + 58} y={y + 54} size={18} fill={COLORS.muted} family="mono" weight={700} letterSpacing={2}>{eyebrow}</Text> : null}
    {children}
  </g>
);

const Citation: React.FC<{ x: number; y: number; text: string; opacity?: number }> = ({ x, y, text, opacity = 1 }) => (
  <g opacity={opacity}>
    <rect x={x} y={y - 19} width={Math.max(46, text.length * 11 + 22)} height={30} rx={15} fill="rgba(110,201,164,0.15)" stroke="rgba(110,201,164,0.52)" strokeWidth={1} />
    <Text x={x + 12} y={y + 2} size={15} fill={COLORS.emerald} family="mono" weight={700}>{text}</Text>
  </g>
);

const Presenter: React.FC<{
  asset: FinanceStealthWealthAsset | undefined;
  fallback: string;
  x: number;
  y: number;
  width: number;
  height: number;
  opacity?: number;
  scale?: number;
  rotate?: number;
}> = ({ asset, fallback, x, y, width, height, opacity = 1, scale = 1, rotate = 0 }) => (
  <image
    href={localAsset(asset, fallback)}
    x={x}
    y={y}
    width={width}
    height={height}
    opacity={opacity}
    preserveAspectRatio="xMidYMid meet"
    transform={`rotate(${rotate} ${x + width / 2} ${y + height / 2}) scale(${scale})`}
    style={{ filter: "drop-shadow(0px 22px 20px rgba(0,0,0,0.38))" }}
  />
);

const World: React.FC<{
  asset: FinanceStealthWealthAsset | undefined;
  fallback: string;
  opacity?: number;
  zoom?: number;
  tint?: string;
}> = ({ asset, fallback, opacity = 1, zoom = 1, tint }) => (
  <g opacity={opacity}>
    <image
      href={localAsset(asset, fallback)}
      x={0}
      y={0}
      width={DESIGN.width}
      height={DESIGN.height}
      preserveAspectRatio="xMidYMid slice"
      transform={`translate(${-(DESIGN.width * (zoom - 1)) / 2} ${-(DESIGN.height * (zoom - 1)) / 2}) scale(${zoom})`}
      style={{ filter: "blur(22px) brightness(0.82) saturate(0.78)" }}
    />
    {tint ? <rect width={DESIGN.width} height={DESIGN.height} fill={tint} opacity={0.22} /> : null}
  </g>
);

const IndexLine: React.FC<{ progress: number; x: number; y: number; width: number; height: number }> = ({ progress, x, y, width, height }) => {
  const points = [
    [0, 0.74], [0.12, 0.7], [0.23, 0.66], [0.34, 0.68], [0.44, 0.55], [0.55, 0.58], [0.64, 0.41], [0.75, 0.47], [0.84, 0.25], [0.93, 0.3], [1, 0.08],
  ];
  const visible = Math.max(2, Math.round((points.length - 1) * clamp01(progress)) + 1);
  const d = points.slice(0, visible).map(([px, py], index) => `${index ? "L" : "M"}${x + px * width} ${y + py * height}`).join(" ");
  return (
    <g>
      <line x1={x} y1={y + height} x2={x + width} y2={y + height} stroke="rgba(242,238,229,0.22)" strokeWidth={2} />
      <line x1={x} y1={y} x2={x} y2={y + height} stroke="rgba(242,238,229,0.22)" strokeWidth={2} />
      <path d={d} fill="none" stroke={COLORS.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={x + points[Math.min(visible - 1, points.length - 1)][0] * width} cy={y + points[Math.min(visible - 1, points.length - 1)][1] * height} r={9} fill={COLORS.amberSoft} />
    </g>
  );
};

const Wafer: React.FC<{ x: number; y: number; scale?: number; opacity?: number }> = ({ x, y, scale = 1, opacity = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`} opacity={opacity}>
    <ellipse cx={0} cy={0} rx={210} ry={210} fill="rgba(38,163,119,0.30)" stroke={COLORS.emerald} strokeWidth={7} />
    {Array.from({ length: 9 }, (_, i) => <ellipse key={`wafer-ring-${i}`} cx={0} cy={0} rx={36 + i * 20} ry={36 + i * 20} fill="none" stroke="rgba(110,201,164,0.32)" strokeWidth={2} />)}
    {Array.from({ length: 12 }, (_, i) => <path key={`wafer-line-${i}`} d={`M${-180 + i * 32} ${-180} L${180 - i * 9} ${180}`} stroke="rgba(231,192,140,0.34)" strokeWidth={2} />)}
    <circle cx={0} cy={0} r={14} fill={COLORS.amberSoft} />
  </g>
);

const TopTenChart: React.FC<{ x: number; y: number; opacity?: number }> = ({ x, y, opacity = 1 }) => (
  <g opacity={opacity}>
    <Text x={x} y={y} size={18} fill={COLORS.muted} family="mono" weight={700} letterSpacing={1.5}>INDEX CONCENTRATION · 2025</Text>
    <Text x={x} y={y + 82} size={76} fill={COLORS.ink} weight={700}>41%</Text>
    <Text x={x + 250} y={y + 79} size={23} fill={COLORS.muted}>TOP TEN WEIGHT</Text>
    <rect x={x} y={y + 110} width={510} height={17} rx={9} fill="rgba(242,238,229,0.17)" />
    <rect x={x} y={y + 110} width={418} height={17} rx={9} fill={COLORS.amber} />
    <Text x={x} y={y + 190} size={68} fill={COLORS.emerald} weight={700}>32%</Text>
    <Text x={x + 250} y={y + 187} size={23} fill={COLORS.muted}>TOP TEN EARNINGS</Text>
    <rect x={x} y={y + 218} width={510} height={17} rx={9} fill="rgba(242,238,229,0.17)" />
    <rect x={x} y={y + 218} width={326} height={17} rx={9} fill={COLORS.emerald} />
    <Text x={x} y={y + 290} size={16} fill={COLORS.muted} family="mono">WEIGHT OUTRUNS EARNINGS CONTRIBUTION</Text>
  </g>
);

const PassiveFunnel: React.FC<{ x: number; y: number; opacity?: number }> = ({ x, y, opacity = 1 }) => (
  <g transform={`translate(${x} ${y})`} opacity={opacity}>
    <path d="M-230 -110 H230 L92 70 V188 H-92 V70 Z" fill="rgba(214,165,107,0.25)" stroke={COLORS.amberSoft} strokeWidth={5} />
    <path d="M-200 -80 H200" stroke={COLORS.amberSoft} strokeWidth={5} />
    <Text x={0} y={-28} size={29} anchor="middle" fill={COLORS.ink} weight={700}>PASSIVE INFLOWS</Text>
    <Text x={0} y={49} size={52} anchor="middle" fill={COLORS.amberSoft} weight={700}>$40 / $100</Text>
    <Text x={0} y={140} size={17} anchor="middle" fill={COLORS.muted} family="mono">DIRECTED TO THE TOP TEN</Text>
    <path d="M0 220 V300" stroke={COLORS.emerald} strokeWidth={8} strokeLinecap="round" />
    <path d="M-20 280 L0 310 L20 280" fill="none" stroke={COLORS.emerald} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
  </g>
);

const Chip: React.FC<{ x: number; y: number; label: string; accent: string; opacity?: number }> = ({ x, y, label, accent, opacity = 1 }) => (
  <g transform={`translate(${x} ${y})`} opacity={opacity}>
    <rect x={-82} y={-56} width={164} height={112} rx={18} fill={COLORS.charcoalSoft} stroke={accent} strokeWidth={5} />
    <rect x={-48} y={-23} width={96} height={46} rx={8} fill={accent} opacity={0.72} />
    {Array.from({ length: 5 }, (_, i) => <line key={`pin-left-${i}`} x1={-95} y1={-38 + i * 19} x2={-82} y2={-38 + i * 19} stroke={accent} strokeWidth={4} />)}
    {Array.from({ length: 5 }, (_, i) => <line key={`pin-right-${i}`} x1={82} y1={-38 + i * 19} x2={95} y2={-38 + i * 19} stroke={accent} strokeWidth={4} />)}
    <Text x={0} y={92} size={19} anchor="middle" fill={COLORS.ink} family="mono" weight={700}>{label}</Text>
  </g>
);

const LowerThird: React.FC<{ text: string; subtext?: string; opacity?: number }> = ({ text, subtext, opacity = 1 }) => (
  <g opacity={opacity}>
    <rect x={112} y={950} width={900} height={76} rx={18} fill="rgba(17,20,23,0.78)" stroke="rgba(242,238,229,0.18)" strokeWidth={2} />
    <rect x={112} y={950} width={7} height={76} rx={3} fill={COLORS.emerald} />
    <Text x={144} y={983} size={18} fill={COLORS.muted} family="mono" weight={700} letterSpacing={1.4}>{text}</Text>
    {subtext ? <Text x={144} y={1011} size={15} fill={COLORS.ink}>{subtext}</Text> : null}
  </g>
);

const SceneOne: React.FC<{ time: number; beat: FinanceStealthWealthBeat; presenter: FinanceStealthWealthAsset | undefined; warm: FinanceStealthWealthAsset | undefined }> = ({ time, beat, presenter, warm }) => {
  const opacity = beatOpacity(time, beat);
  const lineProgress = interpolate(time, [0, 7.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <g opacity={opacity}>
      <World asset={warm} fallback="assets/generated/stealth-wealth-v1/warm-oak-study-v1.png" zoom={1.04} />
      <rect width={DESIGN.width} height={DESIGN.height} fill="#0C1012" opacity={0.18} />
      <GlassCard x={150} y={214} width={780} height={420} eyebrow="S&P 500 INDEX · MARKET PROMISE" accent={COLORS.ink}>
        <Text x={218} y={340} size={58} family="serif" weight={500}>The wealth machine.</Text>
        <Text x={218} y={386} size={25} fill={COLORS.muted}>A strong-looking index. A quiet concentration story.</Text>
        <IndexLine x={220} y={458} width={620} height={120} progress={lineProgress} />
        <Citation x={218} y={605} text="REPORT · ACT VI" />
      </GlassCard>
      <Presenter asset={presenter} fallback="assets/finance-host-presenter-plate-v1.png" x={1135} y={82} width={630} height={990} opacity={0.98} />
      <Text x={1250} y={165} size={18} fill={COLORS.amberSoft} family="mono" weight={700} letterSpacing={2}>CAPITAL / SILICON / COMPUTE</Text>
      <LowerThird text="THE GREAT VALUATION PARADOX" subtext="A market that looks diversified can still share one economic weather system." opacity={opacity} />
    </g>
  );
};

const SceneTwo: React.FC<{ time: number; beat: FinanceStealthWealthBeat; presenter: FinanceStealthWealthAsset | undefined; claims: FinanceStealthWealthClaim[] }> = ({ time, beat, presenter, claims }) => {
  const opacity = beatOpacity(time, beat);
  const cape = claim(claims, "sp500-cape");
  const pe = claim(claims, "memory-forward-pe");
  return (
    <g opacity={opacity}>
      <World asset={undefined} fallback="assets/generated/stealth-wealth-v1/warm-oak-study-v1.png" zoom={1.08} />
      <rect width={DESIGN.width} height={DESIGN.height} fill="#0D1113" opacity={0.34} />
      <GlassCard x={146} y={206} width={640} height={564} eyebrow="THE AUTHORITY HOOK" accent={COLORS.red}>
        <Text x={220} y={356} size={154} fill={COLORS.ink} weight={700} letterSpacing={-5}>41.18</Text>
        <Text x={226} y={403} size={24} fill={COLORS.red} family="mono" weight={700} letterSpacing={1.4}>S&P 500 SHILLER CAPE</Text>
        <Text x={226} y={458} size={23} fill={COLORS.muted}>A level exceeded only once:</Text>
        <Text x={226} y={502} size={35} fill={COLORS.amberSoft} family="serif">the December 1999 peak.</Text>
        <rect x={220} y={560} width={486} height={1} fill="rgba(242,238,229,0.2)" />
        <Text x={226} y={628} size={56} fill={COLORS.emerald} weight={700}>4×–7×</Text>
        <Text x={226} y={672} size={22} fill={COLORS.muted}>MEMORY FORWARD P/E RANGE</Text>
        <Citation x={226} y={728} text={`${cape.citation} · ${pe.citation}`} />
        <title>{cape.claim_text} {pe.claim_text}</title>
      </GlassCard>
      <Presenter asset={presenter} fallback="assets/finance-host-presenter-plate-v1.png" x={1060} y={108} width={680} height={970} opacity={0.98} />
      <Text x={1100} y={194} size={17} fill={COLORS.muted} family="mono" weight={700} letterSpacing={2}>THE CONTRADICTION IS THE STORY</Text>
      <LowerThird text="VALUATION PROFILE" subtext="The report’s comparison is stark: expensive index, compressed memory multiples." opacity={opacity} />
    </g>
  );
};

const SceneThree: React.FC<{ time: number; beat: FinanceStealthWealthBeat; presenter: FinanceStealthWealthAsset | undefined; cool: FinanceStealthWealthAsset | undefined }> = ({ time, beat, presenter, cool }) => {
  const opacity = beatOpacity(time, beat);
  const waferOpacity = interpolate(time, [16, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <g opacity={opacity}>
      <World asset={cool} fallback="assets/generated/stealth-wealth-v1/cool-wafer-lab-v1.png" zoom={1.06} />
      <rect width={DESIGN.width} height={DESIGN.height} fill="#0C1B22" opacity={0.2} />
      <Wafer x={430} y={602} scale={1.05} opacity={waferOpacity} />
      <GlassCard x={128} y={156} width={850} height={366} eyebrow="THE PHYSICAL COUNTERCASE" accent={COLORS.emerald} opacity={0.98}>
        <Text x={200} y={286} size={70} family="serif" weight={500}>The index is lying</Text>
        <Text x={200} y={354} size={70} family="serif" weight={500}>about what is scarce.</Text>
        <Text x={202} y={416} size={24} fill={COLORS.muted}>A crowded weights floor can hide an empty subscription.</Text>
        <Citation x={202} y={472} text="REPORT · ACT I / ACT IV" />
      </GlassCard>
      <Presenter asset={presenter} fallback="assets/finance-host-presenter-plate-v1.png" x={1320} y={250} width={505} height={820} opacity={0.96} />
      <GlassCard x={960} y={676} width={630} height={228} eyebrow="HBM · NOT ORDINARY STORAGE" accent={COLORS.amber} opacity={0.95}>
        <Text x={1025} y={772} size={30} fill={COLORS.ink}>More layers. More failure points.</Text>
        <Text x={1025} y={815} size={21} fill={COLORS.muted}>Scarcity lives in wafers, packaging, time, and yield.</Text>
      </GlassCard>
      <LowerThird text="A PRODUCT CAN BE REAL BEFORE ITS PRICE IS FAIR" subtext="The physical bottleneck is the mechanism to examine." opacity={opacity} />
    </g>
  );
};

const SceneFour: React.FC<{ time: number; beat: FinanceStealthWealthBeat; presenter: FinanceStealthWealthAsset | undefined; claims: FinanceStealthWealthClaim[] }> = ({ time, beat, presenter, claims }) => {
  const opacity = beatOpacity(time, beat);
  const weight = claim(claims, "top-ten-weight");
  const earnings = claim(claims, "top-ten-earnings");
  const passive = claim(claims, "passive-flow");
  return (
    <g opacity={opacity}>
      <World asset={undefined} fallback="assets/generated/stealth-wealth-v1/warm-oak-study-v1.png" zoom={1.06} />
      <rect width={DESIGN.width} height={DESIGN.height} fill="#151A1C" opacity={0.48} />
      <GlassCard x={124} y={126} width={930} height={678} eyebrow="THE CONCENTRATION GAP" accent={COLORS.amber}>
        <TopTenChart x={202} y={220} />
        <Citation x={202} y={760} text={`${weight.citation} · ${earnings.citation}`} />
        <title>{weight.claim_text} {earnings.claim_text}</title>
      </GlassCard>
      <PassiveFunnel x={1368} y={395} opacity={0.98} />
      <Citation x={1190} y={746} text={passive.citation} />
      <Presenter asset={presenter} fallback="assets/finance-host-presenter-plate-v1.png" x={1410} y={122} width={450} height={740} opacity={0.96} />
      <Text x={1220} y={860} size={24} fill={COLORS.ink} family="serif">The index feeds its own weight.</Text>
      <Text x={1220} y={899} size={18} fill={COLORS.muted}>Not a forecast. A mechanism.</Text>
      <LowerThird text="PASSIVE INDEXING" subtext="The largest names receive the largest automatic bid." opacity={opacity} />
    </g>
  );
};

const SceneFive: React.FC<{ time: number; beat: FinanceStealthWealthBeat; presenter: FinanceStealthWealthAsset | undefined; claims: FinanceStealthWealthClaim[] }> = ({ time, beat, presenter, claims }) => {
  const opacity = beatOpacity(time, beat);
  const triopoly = claim(claims, "memory-triopoly");
  const rivals = claim(claims, "thirty-rivals");
  const titleOpacity = interpolate(time, [75, 78], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <g opacity={opacity}>
      <World asset={undefined} fallback="assets/generated/stealth-wealth-v1/warm-oak-study-v1.png" zoom={1.02} />
      <rect width={DESIGN.width} height={DESIGN.height} fill="#121719" opacity={0.4} />
      <GlassCard x={126} y={128} width={1120} height={782} eyebrow="ACT I · THE GREAT VALUATION PARADOX" accent={COLORS.emerald}>
        <Text x={204} y={312} size={76} family="serif" weight={500} opacity={titleOpacity}>S&amp;P 500:</Text>
        <Text x={204} y={392} size={100} fill={COLORS.amberSoft} family="serif" weight={500} opacity={titleOpacity}>THE 1999 ILLUSION</Text>
        <Text x={204} y={462} size={22} fill={COLORS.muted} opacity={titleOpacity}>A historical concentration problem meets a physical memory bottleneck.</Text>
        <rect x={204} y={520} width={910} height={1} fill="rgba(242,238,229,0.24)" opacity={titleOpacity} />
        <Text x={204} y={594} size={25} fill={COLORS.ink} opacity={titleOpacity}>The capital cycle removed more than thirty rivals.</Text>
        <Text x={204} y={636} size={21} fill={COLORS.muted} opacity={titleOpacity}>Three companies now stand at the choke point of compute.</Text>
        <Citation x={204} y={704} text={`${rivals.citation} · ${triopoly.citation}`} opacity={titleOpacity} />
        <title>{rivals.claim_text} {triopoly.claim_text}</title>
      </GlassCard>
      <Presenter asset={presenter} fallback="assets/finance-host-presenter-plate-v1.png" x={1318} y={358} width={520} height={710} opacity={titleOpacity} />
      <Chip x={1310} y={198} label="SAMSUNG" accent={COLORS.amberSoft} opacity={titleOpacity} />
      <Chip x={1510} y={198} label="SK hynix" accent={COLORS.emerald} opacity={titleOpacity} />
      <Chip x={1710} y={198} label="MICRON" accent={COLORS.slate} opacity={titleOpacity} />
      <Text x={1320} y={1020} size={17} fill={COLORS.muted} family="mono" weight={700} letterSpacing={1.2} opacity={titleOpacity}>NEXT: HOW A COMMODITY BECAME A CHOKE POINT</Text>
      <LowerThird text="THE SILENT TRIOPOLY" subtext="The report’s next question: can memory stay scarce when the world needs more compute?" opacity={opacity * titleOpacity} />
    </g>
  );
};

export const defaultFinanceStealthWealthProps: FinanceStealthWealthProofProps = {
  schema_version: "finance_stealth_wealth_proof.v1",
  proof_id: "finance-stealth-wealth-proof-v1",
  duration_s: 105,
  delivery_fps: 24,
  authoring_profile: { width: 1920, height: 1080, fps: 24 },
  render_profile: { width: 1920, height: 1080, fps: 24, label: "authoring-1080p" },
  canonical_audio: { path: "", start_s: 0, volume: 1 },
  presenter_assets: [],
  world_assets: [],
  beats: [
    { id: "hook", start_s: 0, end_s: 8, eyebrow: "HOOK", spoken_job: "Establish the index promise", narration_excerpt: "The market may be labeling the wrong bubble.", source_refs: [] },
    { id: "authority", start_s: 8, end_s: 16, eyebrow: "AUTHORITY HOOK", spoken_job: "Introduce the valuation contradiction", narration_excerpt: "The valuation profile is the contradiction.", source_refs: ["sp500-cape", "memory-forward-pe"] },
    { id: "physical", start_s: 16, end_s: 45, eyebrow: "PHYSICAL COUNTERCASE", spoken_job: "Translate the contradiction through the wafer", narration_excerpt: "The underlying shortage is not imaginary.", source_refs: ["memory-triopoly"] },
    { id: "concentration", start_s: 45, end_s: 75, eyebrow: "CONCENTRATION GAP", spoken_job: "Explain weight versus earnings and passive flows", narration_excerpt: "The index is feeding its own weight.", source_refs: ["top-ten-weight", "top-ten-earnings", "passive-flow"] },
    { id: "triopoly", start_s: 75, end_s: 105, eyebrow: "SILENT TRIOPOLY", spoken_job: "Open the memory-sector mechanism", narration_excerpt: "The capital cycle removed more than thirty rivals.", source_refs: ["thirty-rivals", "memory-triopoly"] },
  ],
  claims: [],
  report_source: { path: "source/Memory Deep Research.txt", sha256: "" },
};

export const calculateFinanceStealthWealthMetadata: CalculateMetadataFunction<FinanceStealthWealthProofProps> = ({ props }) => {
  const profile = props.render_profile || props.authoring_profile;
  const fps = Math.max(1, Math.round(finite(profile.fps, 24)));
  return {
    durationInFrames: Math.max(1, Math.round(props.duration_s * fps)),
    width: Math.max(1, Math.round(finite(profile.width, DESIGN.width))),
    height: Math.max(1, Math.round(finite(profile.height, DESIGN.height))),
    fps,
  };
};

export const FinanceStealthWealthProof: React.FC<FinanceStealthWealthProofProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const time = frame / fps;
  const beats = props.beats.length ? props.beats : defaultFinanceStealthWealthProps.beats;
  const warm = props.world_assets.find((asset) => asset.asset_id === "stealth-wealth-warm-study-v1");
  const cool = props.world_assets.find((asset) => asset.asset_id === "stealth-wealth-cool-wafer-v1");
  const direct = props.presenter_assets.find((asset) => asset.asset_id === "finance-host-presenter-direct-v1") || props.presenter_assets[0];
  const full = props.presenter_assets.find((asset) => asset.asset_id === "finance-host-presenter-plate-v1") || direct;
  const [hook, authority, physical, concentration, triopoly] = beats;
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.charcoal, color: COLORS.ink }}>
      <svg viewBox={`0 0 ${DESIGN.width} ${DESIGN.height}`} width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
        <rect width={DESIGN.width} height={DESIGN.height} fill={COLORS.charcoal} />
        <SceneOne time={time} beat={hook} presenter={full} warm={warm} />
        <SceneTwo time={time} beat={authority} presenter={direct} claims={props.claims} />
        <SceneThree time={time} beat={physical} presenter={full} cool={cool} />
        <SceneFour time={time} beat={concentration} presenter={direct} claims={props.claims} />
        <SceneFive time={time} beat={triopoly} presenter={full} claims={props.claims} />
      </svg>
      {props.canonical_audio.path ? <Audio src={staticFile(props.canonical_audio.path)} volume={props.canonical_audio.volume} /> : null}
    </AbsoluteFill>
  );
};
