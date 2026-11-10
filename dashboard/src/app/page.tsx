"use client";

import dynamic from "next/dynamic";

const RoleSelect = dynamic(() => import("./role-select/page"), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 rounded-[10px] bg-surface-container border border-border-base flex items-center justify-center animate-pulse">
          <span className="material-symbols-outlined text-[22px] text-primary">
            terminal
          </span>
        </div>
        <div className="ide-chip border-primary/30 text-primary text-xs">
          INITIALIZING GATEWAY...
        </div>
      </div>
    </div>
  ),
});

export default function Home() {
  return <RoleSelect />;
}
