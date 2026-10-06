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
      <aside className="w-16 h-screen sticky left-0 top-0 border-r border-border-base flex flex-col items-center py-4 gap-4 bg-surface transition-colors duration-150 ease-in-out hidden md:flex z-40">
        <div className="mb-2">
          <Link 
            href="/role-select" 
            className="w-10 h-10 rounded-[10px] border border-border-base hover:border-primary flex items-center justify-center transition-all duration-200 hover:-translate-y-0.5 bg-surface-container"
            title="DaeMon Gateway"
          >
            <span className="font-mono text-base font-extrabold text-primary">D</span>
          </Link>
        </div>
        
        <nav className="flex flex-col gap-2 flex-grow">
          {isOrchestrator ? (
            <Link 
              href="/orchestrator" 
              className={`w-10 h-10 flex items-center justify-center transition-all duration-150 rounded-[10px] border ${
                pathname === "/orchestrator" 
                  ? "bg-primary text-on-primary border-primary shadow-sm" 
                  : "text-secondary border-transparent hover:text-primary hover:border-border-base hover:bg-surface-container"
              }`}
              title="Orchestrator Jobs"
            >
              <span className="material-symbols-outlined text-[18px]">dashboard</span>
            </Link>
          ) : (
            <Link 
              href="/worker" 
              className={`w-10 h-10 flex items-center justify-center transition-all duration-150 rounded-[10px] border ${
                pathname === "/worker" 
                  ? "bg-primary text-on-primary border-primary shadow-sm" 
                  : "text-secondary border-transparent hover:text-primary hover:border-border-base hover:bg-surface-container"
              }`}
              title="Global Pool"
            >
              <span className="material-symbols-outlined text-[18px]">public</span>
            </Link>
          )}
        </nav>
        
        {/* Disconnect */}
        <Link 
          href="/role-select" 
          className="mt-auto w-10 h-10 flex items-center justify-center text-secondary hover:text-error-crimson hover:bg-error-crimson/10 border border-transparent hover:border-error-crimson/30 transition-all rounded-[10px]" 
          title="Disconnect from Cluster"
        >
          <span className="material-symbols-outlined text-[18px]">logout</span>
        </Link>
      </aside>

      <div className="flex-grow flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-13 w-full sticky top-0 z-50 border-b border-border-base bg-surface flex justify-between items-center px-margin-md transition-all">
          <div className="flex items-center gap-3">
            {/* Mobile Nav Trigger */}
            <button className="md:hidden text-secondary hover:text-primary p-1 rounded-[6px]">
               <span className="material-symbols-outlined text-[20px]">menu</span>
            </button>
            <span className="micro-label text-primary font-bold hidden md:inline">DAEMON_GRID</span>
            <div className="h-4 w-[1px] bg-border-base hidden md:block"></div>
            <nav className="flex items-center gap-2 font-sans text-xs">
              <span className="text-secondary font-medium">Cluster</span>
              <span className="text-border-base">/</span>
              <span className="ide-chip text-primary font-semibold border-primary/30">
                {isOrchestrator ? "Orchestrator Console" : "Worker Node"}
              </span>
            </nav>
          </div>
          
          <div className="flex items-center gap-3">
            {mounted && (
              <button 
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="w-8 h-8 flex items-center justify-center text-secondary hover:text-primary hover:bg-surface-container rounded-[8px] border border-border-base hover:border-primary/40 transition-all"
                title="Toggle Color Theme"
              >
                <span className="material-symbols-outlined text-[16px]">
                  {theme === 'dark' ? 'light_mode' : 'dark_mode'}
                </span>
              </button>
            )}
            
            <div className="ide-chip border-success-emerald/40 text-success-emerald bg-success-emerald/5">
               <span className="active-dot"></span>
               <span>GRID_ONLINE</span>
            </div>
          </div>
        </header>

        <main className="flex-grow overflow-y-auto p-margin-lg custom-scrollbar">
          <div className="max-w-container-max mx-auto space-y-gutter">
            {children}
          </div>
        </main>
        
        <footer className="h-7 w-full border-t border-border-base bg-bg-subtle flex items-center justify-between px-margin-md">
          <div className="flex items-center gap-4">
            <span className="micro-label text-secondary text-[10px]">Heartbeat: 5s window</span>
            <div className="h-3 w-[1px] bg-border-base"></div>
            <span className="micro-label text-secondary text-[10px]">Latency: 12ms</span>
          </div>
          <span className="micro-label text-secondary text-[10px]">DaeMon Grid v2.4</span>
        </footer>
      </div>
    </div>
  );
}
