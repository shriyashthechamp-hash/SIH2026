import type { ReactNode } from "react";

type Accent = "vehicle" | "plate" | "tracking" | "event" | "analytics";

export const accentClasses: Record<Accent, { bg: string; text: string; border: string }> = {
  vehicle: { bg: "bg-vehicle", text: "text-vehicle", border: "border-vehicle" },
  plate: { bg: "bg-plate", text: "text-plate", border: "border-plate" },
  tracking: { bg: "bg-tracking", text: "text-tracking", border: "border-tracking" },
  event: { bg: "bg-event", text: "text-event", border: "border-event" },
  analytics: { bg: "bg-analytics", text: "text-analytics", border: "border-analytics" },
};

export function SectionLabel({ children, light = false }: { children: ReactNode; light?: boolean }) {
  return <p className={`technical-label ${light ? "text-paper/55" : "text-muted-foreground"}`}>{children}</p>;
}

export function AccentDot({ accent, className = "" }: { accent: Accent; className?: string }) {
  return <span className={`inline-block size-3 shrink-0 rounded-full ${accentClasses[accent].bg} ${className}`} />;
}

export function CameraFrame({
  src,
  camera,
  time,
  compact = false,
}: {
  src: string;
  camera: string;
  time: string;
  compact?: boolean;
}) {
  return (
    <div className={`camera-frame group ${compact ? "min-h-44" : "min-h-72"}`}>
      <img src={src} alt={`Illustrative ${camera} traffic camera view`} width={1280} height={768} loading="lazy" />
      <div className="camera-shade" />
      <div className="absolute inset-x-0 top-0 grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 p-4">
        <span className="technical-label truncate text-paper"><AccentDot accent="vehicle" className="mr-2 size-2" />{camera}</span>
        <span className="technical-label shrink-0 text-paper/70">{time}</span>
      </div>
      <div className="detection-box" aria-hidden="true">
        <span>VEHICLE · 0.94</span>
        <div className="plate-box"><span>MH20EE0943</span></div>
      </div>
      <div className="absolute bottom-4 left-4 technical-label text-paper/70">ILLUSTRATIVE · DEMO</div>
    </div>
  );
}

export function CarGlyph({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 54" aria-hidden="true" className={className}>
      <path d="M18 40h84l-5-19-13-9H39L25 22 18 40Z" fill="currentColor" />
      <path d="M42 16h37l10 9H31l11-9Z" fill="currentColor" opacity=".72" />
      <circle cx="35" cy="41" r="8" fill="var(--ink)" stroke="currentColor" strokeWidth="4" />
      <circle cx="87" cy="41" r="8" fill="var(--ink)" stroke="currentColor" strokeWidth="4" />
    </svg>
  );
}