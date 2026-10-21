import Link from "next/link";

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center bg-background p-4"
      suppressHydrationWarning
    >
      <div className="w-full max-w-md border border-border-base bg-surface rounded-[20px] shadow-xl p-8 text-center relative">
        <div className="w-16 h-16 rounded-[16px] bg-surface-container border border-border-base flex items-center justify-center mx-auto mb-4">
          <span className="material-symbols-outlined text-[32px] text-primary">
            error_outline
          </span>
        </div>
        <div className="ide-chip mb-2 border-primary/30 text-primary mx-auto w-fit">
          HTTP_404 // ROUTE_NOT_FOUND
        </div>
        <h1 className="text-2xl font-bold title-tight text-foreground tracking-tight mb-2">
          Node or Route Unreachable
        </h1>
        <p className="font-sans text-xs text-secondary mb-6 leading-relaxed">
          The requested cluster resource or path does not exist on this DaeMon
          orchestrator instance. Verify the URL or return to the gateway.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/"
            className="w-full py-2.5 px-4 rounded-[10px] bg-primary text-on-primary font-sans font-semibold text-xs transition-opacity hover:opacity-90 flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-[16px]">home</span>
            Cluster Gateway
          </Link>
          <Link
            href="/orchestrator"
            className="w-full py-2.5 px-4 rounded-[10px] border border-border-base bg-surface-container text-foreground font-sans font-semibold text-xs hover:border-primary transition-colors flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-[16px]">dashboard</span>
            Orchestrator
          </Link>
        </div>
      </div>
    </div>
  );
}
