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
        setError("Invalid credentials. Use admin/admin");
      }
    } else {
      router.push("/worker");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md border border-border-base bg-surface rounded-lg shadow-sm p-8">
        
        <div className="flex flex-col items-center mb-8">
          <span className="material-symbols-outlined text-[48px] text-primary mb-4">
            terminal
          </span>
          <h1 className="font-mono text-2xl font-bold text-primary tracking-wider">
            GRID_GATEWAY
          </h1>
          <p className="font-sans text-sm text-secondary mt-2">
            Authenticate to access cluster
          </p>
        </div>

        {role === "none" ? (
          <div className="flex flex-col gap-4">
            <button 
              onClick={() => setRole("orchestrator")}
              className="w-full py-4 border-2 border-border-base hover:border-primary bg-surface rounded-md flex flex-col items-center justify-center gap-2 transition-colors group"
            >
              <span className="material-symbols-outlined text-[32px] text-secondary group-hover:text-primary">
                admin_panel_settings
              </span>
              <span className="font-sans font-bold text-primary">Orchestrator</span>
              <span className="font-mono text-xs text-secondary">Manage the grid</span>
            </button>
            
            <button 
              onClick={() => handleLogin({ preventDefault: () => {} } as React.FormEvent)}
              className="w-full py-4 border-2 border-border-base hover:border-success-emerald bg-surface rounded-md flex flex-col items-center justify-center gap-2 transition-colors group"
            >
              <span className="material-symbols-outlined text-[32px] text-secondary group-hover:text-success-emerald">
                memory
              </span>
              <span className="font-sans font-bold text-primary">Worker Node</span>
              <span className="font-mono text-xs text-secondary">Donate compute</span>
            </button>
          </div>
        ) : (
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div className="flex items-center gap-2 mb-2">
              <button 
                type="button" 
                onClick={() => setRole("none")}
                className="text-secondary hover:text-primary material-symbols-outlined text-sm"
              >
                arrow_back
              </button>
              <span className="font-mono text-sm text-primary uppercase">Orchestrator Login</span>
            </div>

            {error && (
              <div className="bg-error-crimson/10 border border-error-crimson text-error-crimson text-sm p-2 rounded">
                {error}
              </div>
            )}

            <div>
              <label className="font-mono text-xs uppercase text-secondary block mb-1">Grid ID</label>
              <input 
                type="text"
                value={id}
                onChange={(e) => setId(e.target.value)}
                className="w-full bg-surface border border-border-base rounded px-3 py-2 font-mono text-sm focus:outline-none focus:border-primary"
                placeholder="admin"
                autoFocus
              />
            </div>
            
            <div>
              <label className="font-mono text-xs uppercase text-secondary block mb-1">Passkey</label>
              <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-surface border border-border-base rounded px-3 py-2 font-mono text-sm focus:outline-none focus:border-primary"
                placeholder="•••••"
              />
            </div>

            <button 
              type="submit"
              className="mt-4 w-full bg-primary text-on-primary font-mono text-sm py-3 rounded hover:opacity-90 transition-opacity"
            >
              INITIALIZE CONNECTION
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
