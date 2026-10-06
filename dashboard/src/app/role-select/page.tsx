"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RoleSelect() {
  const router = useRouter();
  const [role, setRole] = useState<"none" | "worker" | "orchestrator">("none");
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (role === "orchestrator") {
      if (id === "admin" && password === "admin") {
        router.push("/orchestrator");
      } else {
        setError("Invalid credentials. Default is admin / admin");
      }
    } else {
      router.push("/worker");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md border border-border-base bg-surface rounded-[20px] shadow-xl p-8 relative">
        
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-[12px] bg-surface-container border border-border-base flex items-center justify-center mb-4">
            <span className="material-symbols-outlined text-[26px] text-primary">
              terminal
            </span>
          </div>
          <div className="ide-chip mb-2 border-primary/30 text-primary">
            DAEMON_v2.4
          </div>
          <h1 className="text-2xl font-bold title-tight text-foreground tracking-tight">
            Cluster Access Gateway
          </h1>
          <p className="font-sans text-xs text-secondary mt-1 text-center">
            Authenticate to initialize node connection to the distributed grid
          </p>
        </div>

        {role === "none" ? (
          <div className="flex flex-col gap-3">
            <button 
              onClick={() => setRole("orchestrator")}
              className="card-interactive w-full py-4 px-5 border border-border-base hover:border-primary bg-surface-container rounded-[12px] flex items-center gap-4 text-left group"
            >
              <div className="w-10 h-10 rounded-[10px] bg-surface border border-border-base flex items-center justify-center shrink-0 group-hover:border-primary/50 transition-colors">
                <span className="material-symbols-outlined text-[22px] text-secondary group-hover:text-primary transition-colors">
                  admin_panel_settings
                </span>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-sans font-bold text-sm text-foreground group-hover:text-primary transition-colors">Orchestrator</span>
                  <span className="ide-chip text-[10px]">MASTER</span>
                </div>
                <p className="font-sans text-xs text-secondary mt-0.5">Submit tasks, monitor queues & manage nodes</p>
              </div>
            </button>
            
            <button 
              onClick={() => handleLogin({ preventDefault: () => {} } as React.FormEvent)}
              className="card-interactive w-full py-4 px-5 border border-border-base hover:border-success-emerald bg-surface-container rounded-[12px] flex items-center gap-4 text-left group"
            >
              <div className="w-10 h-10 rounded-[10px] bg-surface border border-border-base flex items-center justify-center shrink-0 group-hover:border-success-emerald/50 transition-colors">
                <span className="material-symbols-outlined text-[22px] text-secondary group-hover:text-success-emerald transition-colors">
                  memory
                </span>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-sans font-bold text-sm text-foreground group-hover:text-success-emerald transition-colors">Worker Node</span>
                  <span className="ide-chip text-[10px] text-success-emerald border-success-emerald/30">CLIENT</span>
                </div>
                <p className="font-sans text-xs text-secondary mt-0.5">Donate idle CPU/GPU compute power</p>
              </div>
            </button>
          </div>
        ) : (
          <form onSubmit={handleLogin} className="flex flex-col gap-4 animate-in fade-in duration-150">
            <div className="flex items-center gap-2 mb-1">
              <button 
                type="button" 
                onClick={() => setRole("none")}
                className="text-secondary hover:text-primary p-1 rounded-[6px] transition-colors"
              >
                <span className="material-symbols-outlined text-sm">arrow_back</span>
              </button>
              <span className="micro-label text-primary font-bold">Orchestrator Authentication</span>
            </div>

            {error && (
              <div className="bg-error-crimson/10 border border-error-crimson/40 text-error-crimson text-xs p-3 rounded-[8px] font-mono">
                {error}
              </div>
            )}

            <div>
              <label className="micro-label text-secondary block mb-1">Grid ID</label>
              <input 
                type="text"
                value={id}
                onChange={(e) => setId(e.target.value)}
                className="w-full bg-surface-container border border-border-base rounded-[6px] px-3 py-2 font-mono text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                placeholder="admin"
                autoFocus
              />
            </div>
            
            <div>
              <label className="micro-label text-secondary block mb-1">Passkey</label>
              <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-surface-container border border-border-base rounded-[6px] px-3 py-2 font-mono text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                placeholder="•••••"
              />
            </div>

            <button 
              type="submit"
              className="btn-interactive mt-2 w-full bg-primary text-on-primary micro-label font-bold py-2.5 rounded-[8px] border border-primary shadow-sm hover:opacity-95"
            >
              INITIALIZE CONNECTION
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
