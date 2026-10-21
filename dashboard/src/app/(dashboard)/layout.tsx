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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => setMounted(true), []);
  useEffect(() => setMobileMenuOpen(false), [pathname]);

  return (
    <div className="flex min-h-screen overflow-x-hidden bg-background">
      {/* Side Navigation (Desktop) */}
      <aside className="w-16 h-screen sticky left-0 top-0 border-r border-border-base flex flex-col items-center py-4 gap-4 bg-surface transition-colors duration-150 ease-in-out hidden md:flex z-40 shrink-0">
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
          <Link 
            href="/orchestrator" 
            className={`w-10 h-10 flex items-center justify-center transition-all duration-150 rounded-[10px] border ${
              isOrchestrator 
                ? "bg-primary text-on-primary border-primary shadow-sm" 
                : "text-secondary border-transparent hover:text-primary hover:border-border-base hover:bg-surface-container"
            }`}
            title="Orchestrator Console"
          >
            <span className="material-symbols-outlined text-[18px]">dashboard</span>
          </Link>
          <Link 
            href="/worker" 
            className={`w-10 h-10 flex items-center justify-center transition-all duration-150 rounded-[10px] border ${
              !isOrchestrator 
                ? "bg-primary text-on-primary border-primary shadow-sm" 
                : "text-secondary border-transparent hover:text-primary hover:border-border-base hover:bg-surface-container"
            }`}
            title="Worker Node Pool"
          >
            <span className="material-symbols-outlined text-[18px]">public</span>
          </Link>
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

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div 
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity" 
            onClick={() => setMobileMenuOpen(false)} 
          />
          <div className="relative w-64 max-w-[80vw] bg-surface border-r border-border-base h-full flex flex-col p-4 z-10 shadow-2xl animate-in slide-in-from-left duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-border-base mb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-[8px] bg-surface-container border border-border-base flex items-center justify-center">
                  <span className="font-mono text-sm font-extrabold text-primary">D</span>
                </div>
                <span className="micro-label font-bold text-primary">DAEMON_GRID</span>
              </div>
              <button 
                onClick={() => setMobileMenuOpen(false)}
                className="text-secondary hover:text-foreground p-1 rounded-[6px]"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>

            <nav className="flex flex-col gap-2 flex-grow">
              <Link 
                href="/orchestrator" 
                className={`flex items-center gap-3 px-3 py-2.5 rounded-[10px] text-xs font-sans font-medium transition-all border ${
                  isOrchestrator 
                    ? "bg-primary text-on-primary border-primary font-bold shadow-sm" 
                    : "text-secondary hover:text-foreground hover:bg-surface-container border-transparent"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">dashboard</span>
                Orchestrator Console
              </Link>
              <Link 
                href="/worker" 
                className={`flex items-center gap-3 px-3 py-2.5 rounded-[10px] text-xs font-sans font-medium transition-all border ${
                  !isOrchestrator 
                    ? "bg-primary text-on-primary border-primary font-bold shadow-sm" 
                    : "text-secondary hover:text-foreground hover:bg-surface-container border-transparent"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">public</span>
                Worker Node Pool
              </Link>
              <Link 
                href="/role-select" 
                className="flex items-center gap-3 px-3 py-2.5 rounded-[10px] text-xs font-sans font-medium text-secondary hover:text-foreground hover:bg-surface-container transition-all border border-transparent"
              >
                <span className="material-symbols-outlined text-[18px]">swap_horiz</span>
                Switch Role / Gateway
              </Link>
            </nav>

            <div className="pt-4 border-t border-border-base flex flex-col gap-2">
              <div className="flex items-center justify-between text-xs px-2 py-1">
                <span className="text-secondary">Theme</span>
                {mounted && (
                  <button 
                    onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                    className="p-1.5 rounded-[6px] border border-border-base text-secondary hover:text-primary bg-surface-container flex items-center justify-center"
                  >
                    <span className="material-symbols-outlined text-[16px]">
                      {theme === 'dark' ? 'light_mode' : 'dark_mode'}
                    </span>
                  </button>
                )}
              </div>
              <Link 
                href="/role-select" 
                className="flex items-center justify-center gap-2 px-3 py-2 rounded-[8px] text-xs micro-label text-error-crimson hover:bg-error-crimson/10 border border-error-crimson/30 transition-all font-bold"
              >
                <span className="material-symbols-outlined text-[16px]">logout</span>
                Disconnect
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="flex-grow flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-14 w-full sticky top-0 z-30 border-b border-border-base bg-surface flex justify-between items-center px-3 sm:px-margin-md transition-all">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            {/* Mobile Nav Trigger */}
            <button 
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden text-secondary hover:text-primary p-1.5 rounded-[6px] hover:bg-surface-container flex items-center justify-center shrink-0"
              title="Open Navigation"
            >
               <span className="material-symbols-outlined text-[20px]">menu</span>
            </button>
            <span className="micro-label text-primary font-bold hidden sm:inline shrink-0">DAEMON_GRID</span>
            <div className="h-4 w-[1px] bg-border-base hidden sm:block shrink-0"></div>
            <nav className="flex items-center gap-1.5 sm:gap-2 font-sans text-xs min-w-0">
              <span className="text-secondary font-medium hidden xs:inline shrink-0">Cluster</span>
              <span className="text-border-base hidden xs:inline shrink-0">/</span>
              <span className="ide-chip text-primary font-semibold border-primary/30 truncate max-w-[130px] sm:max-w-none">
                {isOrchestrator ? "Orchestrator Console" : "Worker Node"}
              </span>
            </nav>
          </div>
          
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
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
            
            <div className="ide-chip border-success-emerald/40 text-success-emerald bg-success-emerald/5 shrink-0">
               <span className="active-dot"></span>
               <span className="hidden xs:inline">GRID_ONLINE</span>
               <span className="xs:hidden">LIVE</span>
            </div>
          </div>
        </header>

        <main className="flex-grow overflow-y-auto p-3.5 sm:p-5 lg:p-margin-lg custom-scrollbar">
          <div className="max-w-container-max mx-auto space-y-gutter">
            {children}
          </div>
        </main>
        
        <footer className="h-7 w-full border-t border-border-base bg-bg-subtle flex items-center justify-between px-3 sm:px-margin-md shrink-0">
          <div className="flex items-center gap-3 sm:gap-4 truncate">
            <span className="micro-label text-secondary text-[10px]">Heartbeat: 5s</span>
            <div className="h-3 w-[1px] bg-border-base"></div>
            <span className="micro-label text-secondary text-[10px] hidden sm:inline">Latency: 12ms</span>
          </div>
          <span className="micro-label text-secondary text-[10px] shrink-0">DaeMon v2.4</span>
        </footer>
      </div>
    </div>
  );
}
