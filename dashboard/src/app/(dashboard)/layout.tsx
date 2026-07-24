"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isOrchestrator = pathname?.includes("/orchestrator");
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  return (
    <div className="flex min-h-screen overflow-hidden bg-background">
      {/* Side Navigation */}
      <aside className="w-16 h-screen sticky left-0 top-0 border-r border-border-base flex flex-col items-center py-4 gap-4 bg-surface transition-colors duration-150 ease-in-out hidden md:flex">
        <div className="mb-4">
          <span className="font-sans text-lg font-bold text-primary">G</span>
        </div>
        <nav className="flex flex-col gap-2 flex-grow">
          {isOrchestrator ? (
            <>
              <Link 
                href="/orchestrator" 
                className={`w-10 h-10 flex items-center justify-center transition-colors duration-150 ease-in-out rounded-md ${pathname === "/orchestrator" ? "bg-primary text-on-primary" : "text-secondary hover:text-primary hover:bg-surface-container"}`}
                title="My Jobs"
              >
                <span className="material-symbols-outlined text-sm">dashboard</span>
              </Link>
            </>
          ) : (
            <>
              <Link 
                href="/worker" 
                className={`w-10 h-10 flex items-center justify-center transition-colors duration-150 ease-in-out rounded-md ${pathname === "/worker" ? "bg-primary text-on-primary" : "text-secondary hover:text-primary hover:bg-surface-container"}`}
                title="Global Pool"
              >
                <span className="material-symbols-outlined text-sm">public</span>
              </Link>
            </>
          )}
        </nav>
        
        {/* Logout */}
        <Link href="/role-select" className="mt-auto w-10 h-10 flex items-center justify-center text-secondary hover:text-error-crimson hover:bg-error-crimson/10 transition-colors rounded-md" title="Disconnect">
          <span className="material-symbols-outlined text-sm">logout</span>
        </Link>
      </aside>

      <div className="flex-grow flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-12 w-full sticky top-0 z-50 border-b border-border-base bg-surface flex justify-between items-center px-margin-md transition-all duration-100">
          <div className="flex items-center gap-4">
            {/* Mobile Nav Trigger (hidden on md) */}
            <button className="md:hidden text-secondary hover:text-primary">
               <span className="material-symbols-outlined">menu</span>
            </button>
            <span className="font-mono text-xs uppercase tracking-widest text-primary hidden md:inline">GRID_CONSOLE</span>
            <div className="h-4 w-[1px] bg-border-base hidden md:block"></div>
            <nav className="flex items-center gap-4 font-sans text-xs font-medium">
              <span className="text-on-surface-variant">Grid</span>
              <span className="text-secondary">/</span>
              <span className="text-primary font-bold border-b border-primary">{isOrchestrator ? "Orchestrator" : "Worker"}</span>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            {mounted && (
              <button 
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="w-8 h-8 flex items-center justify-center text-secondary hover:text-primary hover:bg-surface-container rounded transition-colors"
                title="Toggle Theme"
              >
                <span className="material-symbols-outlined text-[18px]">
                  {theme === 'dark' ? 'light_mode' : 'dark_mode'}
                </span>
              </button>
            )}
            <span className="font-mono text-[10px] text-success-emerald uppercase flex items-center gap-1.5 border border-border-base px-2 py-1 rounded bg-surface">
               <span className="active-dot"></span>
               Connected
            </span>
          </div>
        </header>

        <main className="flex-grow overflow-y-auto p-margin-lg custom-scrollbar">
          <div className="max-w-container-max mx-auto space-y-gutter">
            {children}
          </div>
        </main>
        
        <footer className="h-6 w-full border-t border-border-base bg-bg-subtle flex items-center justify-between px-margin-md">
          <div className="flex items-center gap-4">
            <span className="font-mono text-[10px] uppercase text-secondary">Latency: 14ms</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
