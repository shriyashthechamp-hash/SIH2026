import { Link } from "react-router-dom";
import { ArrowDown, ArrowRight } from "lucide-react";

import camera01 from "@/assets/camera-01.jpg";
import camera02 from "@/assets/camera-02.jpg";
import camera03 from "@/assets/camera-03.jpg";
import globeAsset from "@/assets/anvay-globe.mp4.asset.json";
import { AccentDot, CameraFrame, SectionLabel, accentClasses } from "@/components/anvay/shared";
import { Button } from "@/components/ui/button";

const capabilities = [
  { n: "01", title: "Vehicle detection", copy: "Locate and classify vehicles in every frame across the urban camera mesh.", accent: "vehicle" as const, span: "md:col-span-6" },
  { n: "02", title: "Number plate recognition", copy: "Detect plates and read alphanumeric strings with per-character confidence.", accent: "plate" as const, span: "md:col-span-6" },
  { n: "03", title: "Vehicle re-identification", copy: "Recognize the same vehicle across cameras without relying on the plate alone.", accent: "tracking" as const, span: "md:col-span-4" },
  { n: "04", title: "Cross-camera tracking", copy: "Link observations into one coherent object identity across the network.", accent: "vehicle" as const, span: "md:col-span-4" },
  { n: "05", title: "Trajectory reconstruction", copy: "Rebuild the path a vehicle took between any two cameras over time.", accent: "tracking" as const, span: "md:col-span-4" },
  { n: "06", title: "Traffic analytics", copy: "Turn isolated journeys into city-scale mobility intelligence.", accent: "analytics" as const, span: "md:col-span-12" },
];

const signals = [
  { n: "01", title: "Plate", copy: "OCR string match", accent: "plate" as const },
  { n: "02", title: "Appearance", copy: "Color · type · shape", accent: "vehicle" as const },
  { n: "03", title: "Time", copy: "Detection window", accent: "event" as const },
  { n: "04", title: "Distance", copy: "Travel feasibility", accent: "tracking" as const },
];

const architecture = [
  ["Cameras", "Urban capture mesh", "vehicle"], ["Vehicle detection", "Frame-level localization", "vehicle"],
  ["Plate detection + OCR", "String extraction", "plate"], ["Vehicle re-identification", "Visual identity", "tracking"],
  ["Cross-camera matching", "Identity fusion", "tracking"], ["Trajectory engine", "Journey reconstruction", "event"],
  ["ANVAY Intelligence OS", "Operator surface", "analytics"],
] as const;

export function LandingPage() {
  return <main className="overflow-hidden bg-paper">
    <Hero />
    <Problem />
    <Capabilities />
    <Matching />
    <Journey />
    <Observation />
    <LivePreview />
    <Architecture />
    <FinalCta />
  </main>;
}

function Hero() {
  return <section className="relative min-h-[100svh] overflow-hidden bg-ink text-paper">
    <div className="absolute inset-0 starfield opacity-35" />
    <div className="globe-fallback absolute -right-[12vw] top-[8vh] aspect-square w-[78vw] opacity-60" />
    <video aria-hidden="true" className="absolute inset-0 size-full object-cover opacity-55" autoPlay muted loop playsInline disablePictureInPicture preload="metadata">
      <source src={globeAsset.url} type="video/mp4" />
    </video>
    <div className="absolute inset-0 bg-[linear-gradient(90deg,var(--ink)_0%,color-mix(in_oklab,var(--ink)_82%,transparent)_43%,color-mix(in_oklab,var(--ink)_28%,transparent)_100%)]" />
    <nav className="page-shell relative z-10 grid grid-cols-[minmax(0,1fr)_auto] items-center border-b border-paper/20 py-5">
      <a href="#top" className="text-xl font-bold tracking-normal">ANVAY</a>
      <div className="flex items-center gap-3 sm:gap-7">
        <a href="#intelligence" className="technical-label hidden text-paper/65 transition-colors hover:text-paper sm:block">Intelligence</a>
        <Button asChild variant="hero" size="sm"><Link to="/demo">Test prototype <ArrowRight /></Link></Button>
      </div>
    </nav>
    <div id="top" className="page-shell relative z-10 flex min-h-[calc(100svh-82px)] flex-col justify-end pb-12 pt-24 sm:pb-16">
      <div className="mb-auto flex justify-between pt-8">
        <SectionLabel light>Multi-camera · vehicle intelligence</SectionLabel>
        <SectionLabel light>Visual system · illustrative</SectionLabel>
      </div>
      <p className="technical-label mb-5 text-vehicle">City-wide vehicle intelligence</p>
      <h1 className="display-title max-w-6xl">ANVAY</h1>
      <div className="mt-7 grid gap-8 border-t border-paper/25 pt-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
        <p className="max-w-2xl text-xl leading-relaxed text-paper/75 sm:text-2xl">Connect vehicles, cameras and observations into continuous, explainable journeys.</p>
        <div className="flex flex-wrap gap-3">
          <Button asChild variant="hero" size="lg"><Link to="/demo">Test the prototype <ArrowRight /></Link></Button>
          <Button asChild variant="ghost" size="lg" className="font-mono text-xs uppercase tracking-[0.16em] text-paper hover:bg-paper/10 hover:text-paper"><a href="#problem">Explore ANVAY <ArrowDown /></a></Button>
        </div>
      </div>
    </div>
  </section>;
}

function Problem() {
  const cards = [
    ["Camera 01", "Vehicle detected", "vehicle"], ["Camera 02", "Same vehicle", "tracking"], ["Camera 03", "Continuous journey", "analytics"],
  ] as const;
  return <section id="problem" className="editorial-section border-b-2 border-ink">
    <div className="page-shell">
      <SectionLabel>02 — The problem</SectionLabel>
      <h2 className="section-title mt-10">A vehicle doesn’t stop existing when it leaves one camera’s frame.</h2>
      <p className="mt-7 max-w-3xl text-lg leading-relaxed text-muted-foreground">Most systems see isolated snapshots. ANVAY sees the vehicle between them — and turns disconnected detections into one continuous, explainable journey.</p>
      <div className="relative mt-16 grid gap-7 md:grid-cols-3">
        <div className="absolute left-[8%] right-[8%] top-1/2 hidden h-0.5 bg-ink md:block" />
        {cards.map(([camera, title, accent]) => <article key={camera} className="physical-card relative z-10 flex min-h-52 flex-col justify-between p-7 sm:p-9">
          <SectionLabel>{camera}</SectionLabel>
          <div>
            <h3 className="flex items-center gap-3 text-2xl font-bold uppercase"><AccentDot accent={accent} />{title}</h3>
            <div className={`mt-7 h-1.5 w-full rounded-full ${accentClasses[accent].bg}`} />
          </div>
        </article>)}
      </div>
    </div>
  </section>;
}

function Capabilities() {
  return <section id="intelligence" className="editorial-section">
    <div className="page-shell">
      <SectionLabel>03 — ANVAY capabilities</SectionLabel>
      <h2 className="section-title mt-10">One intelligence system.<br />Six connected capabilities.</h2>
      <div className="mt-16 grid grid-cols-1 gap-6 md:grid-cols-12">
        {capabilities.map((item) => <article key={item.n} className={`physical-card flex min-h-64 flex-col p-7 sm:p-9 ${item.span}`}>
          <div className="flex items-center justify-between"><SectionLabel>{item.n}</SectionLabel><span className={`h-3 w-14 rounded-full ${accentClasses[item.accent].bg}`} /></div>
          <h3 className="mt-10 max-w-2xl text-2xl font-bold uppercase leading-tight sm:text-3xl">{item.title}</h3>
          <p className="mt-4 max-w-3xl text-base leading-relaxed text-muted-foreground">{item.copy}</p>
          <div className={`mt-auto h-7 rounded-full pt-7 ${accentClasses[item.accent].bg}`} />
        </article>)}
      </div>
    </div>
  </section>;
}

function Matching() {
  return <section className="editorial-section border-y-2 border-ink bg-surface">
    <div className="page-shell">
      <SectionLabel>04 — How ANVAY thinks</SectionLabel>
      <h2 className="section-title mt-10">Matching is never one signal. It’s four, weighted together.</h2>
      <p className="mt-7 max-w-3xl text-lg leading-relaxed text-muted-foreground">ANVAY does not rely on OCR alone. Independent signals contribute to a single, explainable match confidence — so a missed plate never breaks a journey.</p>
      <div className="mt-16 grid gap-5 lg:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr] lg:items-center">
        {signals.map((signal, i) => <div key={signal.n} className="contents">
          <article className={`physical-card min-h-48 border-t-8 p-7 ${accentClasses[signal.accent].border}`}>
            <SectionLabel>Signal {signal.n}</SectionLabel><h3 className="mt-5 text-2xl font-bold uppercase">{signal.title}</h3><p className="technical-label mt-3 text-muted-foreground">{signal.copy}</p>
          </article>
          {i < 3 && <span className="hidden text-3xl font-bold lg:block">+</span>}
        </div>)}
      </div>
      <div className="dark-panel mt-8 grid gap-12 p-8 sm:p-12 lg:grid-cols-2 lg:items-end">
        <div><SectionLabel light>Output</SectionLabel><h3 className="mt-6 text-4xl font-bold uppercase sm:text-5xl">Match confidence</h3><p className="mt-5 max-w-xl text-paper/60">A single, auditable score — decomposable into the signals that produced it.</p></div>
        <div><div className="flex items-end justify-between"><SectionLabel light>Confidence</SectionLabel><strong className="text-6xl text-vehicle">94</strong></div><div className="mt-4 h-3 rounded-full border border-paper/30 p-0.5"><div className="h-full w-[94%] rounded-full bg-vehicle" /></div><div className="technical-label mt-3 flex justify-between text-paper/45"><span>0</span><span>Illustrative</span><span>100</span></div></div>
      </div>
    </div>
  </section>;
}

function Journey() {
  return <section className="editorial-section">
    <div className="page-shell">
      <SectionLabel>05 — Multi-camera intelligence</SectionLabel><h2 className="section-title mt-10">Observations become a journey.</h2>
      <div className="physical-card mt-14 overflow-hidden bg-surface">
        <div className="grid grid-cols-[minmax(0,1fr)_auto] border-b-2 border-ink px-5 py-4"><SectionLabel>Network view · illustrative</SectionLabel><SectionLabel>Vehicle A · demo</SectionLabel></div>
        <div className="relative min-h-[34rem] overflow-hidden p-4 sm:p-10">
          <svg viewBox="0 0 1080 400" className="absolute inset-0 size-full" preserveAspectRatio="none" aria-hidden="true"><path d="M 85 285 C 270 225, 360 140, 510 120 S 820 265, 995 300" fill="none" stroke="currentColor" strokeWidth="2" className="animate-draw" /></svg>
          <div className="animate-travel absolute size-5 rounded-full border-4 border-vehicle bg-ink" />
          {[{x:"left-[5%]",y:"top-[65%]",cam:"CAM-01",a:"bg-vehicle"},{x:"left-[45%]",y:"top-[20%]",cam:"CAM-02",a:"bg-plate"},{x:"right-[5%]",y:"top-[68%]",cam:"CAM-03",a:"bg-tracking"}].map((n: any) => <div key={n.cam} className={`absolute ${n.x} ${n.y} flex -translate-x-1/2 flex-col items-center gap-4`}><span className="grid size-16 place-items-center rounded-full border-2 border-ink bg-surface"><span className={`size-5 rounded-full border-2 border-ink ${n.a}`} /></span><SectionLabel>{n.cam}</SectionLabel></div>)}
        </div>
        <div className="grid border-t-2 border-ink sm:grid-cols-3">{["CAM-01","CAM-02","CAM-03"].map((cam,i)=><div key={cam} className={`p-5 ${i ? "border-t-2 sm:border-l-2 sm:border-t-0" : ""}`}><SectionLabel>{cam}</SectionLabel><p className="mt-2 font-semibold">observation</p></div>)}</div>
      </div>
    </div>
  </section>;
}

function Observation() {
  const record = [["Vehicle","Car","vehicle"],["Plate","MH20EE0943","plate"],["Color","Blue","tracking"],["Camera","CAM-02","analytics"],["Time","14:32:08","event"]] as const;
  return <section className="editorial-section border-y-2 border-ink bg-surface"><div className="page-shell">
    <SectionLabel>06 — Observation</SectionLabel><h2 className="section-title mt-10">A single observation,<br />fully described.</h2>
    <div className="mt-14 grid gap-8 lg:grid-cols-[1.35fr_.95fr]">
      <div className="dark-panel p-5 sm:p-8"><div className="mb-6 flex justify-between"><SectionLabel light>CAM-02 · frame 00428</SectionLabel><span className="technical-label rounded-full border border-event px-3 py-1 text-event">Illustrative · demo</span></div><CameraFrame src={camera02} camera="CAM-02" time="14:32:08" /></div>
      <div className="physical-card bg-paper p-7 sm:p-9"><SectionLabel>Observation record</SectionLabel><dl className="mt-7">{record.map(([k,v,a])=><div key={k} className="grid grid-cols-[minmax(0,1fr)_auto] items-center border-b border-ink/15 py-5"><dt className="technical-label text-muted-foreground">{k}</dt><dd className="flex items-center gap-3 text-lg font-bold uppercase"><AccentDot accent={a as any} className="size-2.5" />{v}</dd></div>)}</dl><div className="mt-5"><div className="flex justify-between"><SectionLabel>Confidence</SectionLabel><strong className="text-xl">94%</strong></div><div className="mt-3 h-2 rounded-full bg-surface"><div className="h-full w-[94%] rounded-full bg-vehicle" /></div></div><div className="mt-8 rounded-xl border-2 border-ink bg-surface p-5"><SectionLabel>Journey</SectionLabel><p className="technical-label mt-3 text-ink">CAM-01 → CAM-02 → CAM-03</p></div></div>
    </div>
  </div></section>;
}

function LivePreview() {
  return <section className="editorial-section"><div className="page-shell">
    <SectionLabel>07 — Live system preview</SectionLabel><div className="mt-8 grid gap-7 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center"><h2 className="section-title">The ANVAY Intelligence OS.</h2><Button asChild variant="editorial" size="lg"><Link to="/demo">See ANVAY in action <ArrowRight /></Link></Button></div>
    <div className="dark-panel mt-12 overflow-hidden border-2 border-ink shadow-hard-lg">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center border-b border-paper/20 px-5 py-4"><div className="flex min-w-0 items-center gap-5"><div className="flex shrink-0 gap-2"><span className="size-3 rounded-full bg-tracking"/><span className="size-3 rounded-full bg-event"/><span className="size-3 rounded-full bg-vehicle"/></div><SectionLabel light>ANVAY · Intelligence OS</SectionLabel></div><span className="technical-label text-vehicle"><AccentDot accent="vehicle" className="mr-2 size-2"/>Demo</span></div>
      <div className="grid gap-6 p-5 lg:grid-cols-[2fr_1fr] lg:p-8"><div><SectionLabel light>Camera network · sample feeds</SectionLabel><div className="mt-5 grid gap-4 sm:grid-cols-2"><CameraFrame src={camera01} camera="CAM-01" time="14:32" compact/><CameraFrame src={camera02} camera="CAM-02" time="14:35" compact/><CameraFrame src={camera03} camera="CAM-03" time="14:39" compact/><CameraFrame src={camera01} camera="CAM-04" time="standby" compact/></div></div><div className="space-y-5"><div className="rounded-xl border-2 border-paper/20 bg-paper/5 p-6"><SectionLabel light>Active vehicle · sample</SectionLabel><p className="mt-4 text-3xl font-bold">A-042 · CAR</p><p className="technical-label mt-3 text-paper/55">MH20EE0943 · BLUE</p><p className="technical-label mt-5 text-paper/55">CAM-01 → CAM-02 → CAM-03</p></div><div className="rounded-xl border-2 border-paper/20 bg-paper/5 p-6"><SectionLabel light>Events · sample</SectionLabel>{["14:32 · detected","14:35 · matched","14:39 · journey"].map(x=><p key={x} className="technical-label mt-5 text-paper/65"><AccentDot accent="event" className="mr-3 size-2"/>{x}</p>)}</div></div></div>
    </div>
  </div></section>;
}

function Architecture() {
  return <section className="editorial-section border-y-2 border-ink bg-surface"><div className="page-shell"><SectionLabel>08 — Technical architecture</SectionLabel><h2 className="section-title mt-10">From photons to journeys.</h2><div className="mt-14 border-2 border-ink bg-paper"><div className="grid lg:grid-cols-7">{architecture.map(([title,copy,accent],i)=><article key={title} className={`relative min-h-56 border-ink p-6 ${i ? "border-t-2 lg:border-l-2 lg:border-t-0" : ""}`}><span className={`grid size-12 place-items-center rounded-full border-2 border-ink font-mono font-bold ${accentClasses[accent as keyof typeof accentClasses].bg}`}>{String(i+1).padStart(2,"0")}</span><h3 className="mt-8 text-lg font-bold uppercase leading-tight">{title}</h3><p className="technical-label mt-4 text-muted-foreground">{copy}</p>{i<6&&<ArrowRight className="absolute -bottom-4 right-5 z-10 size-8 rounded-full border-2 border-ink bg-surface p-1 lg:-right-4 lg:bottom-5"/>}</article>)}</div></div></div></section>;
}

function FinalCta() {
  return <section className="editorial-section"><div className="page-shell"><SectionLabel>09 — Enter ANVAY</SectionLabel><h2 className="mt-10 max-w-7xl text-[clamp(3.6rem,9vw,9rem)] font-bold uppercase leading-[.88]">See the vehicle.<br/>Understand<br/>the journey.</h2><div className="mt-12 flex border-t-2 border-ink pt-8"><Button asChild variant="editorial" size="lg"><Link to="/demo">Test the prototype <ArrowRight /></Link></Button></div><footer className="mt-28 flex flex-col justify-between gap-5 border-t border-ink pt-6 sm:flex-row"><strong>ANVAY</strong><SectionLabel>City-wide vehicle intelligence · Frontend prototype</SectionLabel></footer></div></section>;
}
