"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";

export default function OrchestratorJobDetails({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    "[SYSTEM] Connection established to grid orchestrator.",
    `[INFO] Job ${resolvedParams.id} initialized. Splitting payload into 100 chunks.`,
    "[INFO] Pushing chunks to RabbitMQ public_pool...",
  ]);
  const [showWorkers, setShowWorkers] = useState(false);

  // Mock a live terminal feed
  useEffect(() => {
    const events = [
      "[WORKER] NODE-774A connected to pool.",
      "[WORKER] NODE-774A started chunk 1.",
      "[WORKER] NODE-112B connected to pool.",
      "[WORKER] NODE-112B started chunk 2.",
      "[SUCCESS] NODE-774A completed chunk 1 in 2.4s",
      "[INFO] Grid progress: 2/100 chunks.",
      "[WARNING] NODE-999C timeout. Re-queueing chunk 3."
    ];
    let i = 0;
    const interval = setInterval(() => {
      if (i < events.length) {
        setTerminalLogs(prev => [...prev, events[i]]);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col md:flex-row gap-6 h-[calc(100vh-140px)]">
      
      {/* Left Column: Metrics & Controls */}
      <div className="w-full md:w-1/2 flex flex-col gap-6">
        
        {/* Header */}
        <div>
          <Link href="/orchestrator" className="text-secondary hover:text-primary font-mono text-xs uppercase flex items-center gap-1 mb-4">
            <span className="material-symbols-outlined text-[14px]">arrow_back</span>
            Back to Jobs
          </Link>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold font-sans text-primary">Job #{resolvedParams.id}</h1>
            <span className="bg-success-emerald/10 text-success-emerald border border-success-emerald/20 px-2 py-0.5 rounded text-xs font-mono uppercase">Active</span>
          </div>
          <p className="text-sm font-mono text-secondary">Hash Verifier Batch A</p>
        </div>

        {/* Big Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Total Progress</span>
            <span className="text-3xl font-bold font-sans text-primary">78<span className="text-lg text-secondary">%</span></span>
            <div className="w-full bg-surface-container h-1 mt-2">
              <div className="bg-success-emerald h-1" style={{ width: '78%' }}></div>
            </div>
          </div>
          
          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Active Workers</span>
            <span className="text-3xl font-bold font-sans text-primary">42</span>
            <span className="font-mono text-[10px] text-success-emerald mt-1">+3 joined recently</span>
          </div>

          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Time Elapsed</span>
            <span className="text-3xl font-bold font-sans text-primary">14<span className="text-lg text-secondary">m</span> 22<span className="text-lg text-secondary">s</span></span>
          </div>
          
          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Est. Completion</span>
            <span className="text-3xl font-bold font-sans text-primary">4<span className="text-lg text-secondary">m</span></span>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-surface border border-border-base rounded-sm overflow-hidden mt-auto">
          <div className="bg-surface border-b border-border-base px-4 py-3 flex justify-between items-center">
             <span className="font-mono text-xs uppercase text-primary font-bold">Admin Controls</span>
          </div>
          <div className="p-4 flex flex-wrap gap-3">
            <button 
              onClick={() => setShowWorkers(!showWorkers)}
              className="px-4 py-2 bg-surface text-primary border border-border-base hover:border-primary transition-colors font-mono text-xs uppercase rounded-sm flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[16px]">group</span>
              View Connected Workers
            </button>
            <button className="px-4 py-2 bg-error-crimson/10 text-error-crimson border border-error-crimson/30 hover:bg-error-crimson hover:text-on-error transition-colors font-mono text-xs uppercase rounded-sm flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px]">stop_circle</span>
              Halt Entire Task
            </button>
          </div>
        </div>

        {/* View Workers Panel (Toggled) */}
        {showWorkers && (
          <div className="bg-surface border border-border-base rounded-sm p-4 animate-in fade-in slide-in-from-top-4">
             <h3 className="font-mono text-xs uppercase text-secondary mb-3">Active Node Roster</h3>
             <div className="space-y-2">
               <div className="flex justify-between items-center text-sm border-b border-border-base/50 pb-2">
                 <span className="font-mono text-primary font-bold">NODE-774A</span>
                 <span className="text-secondary font-mono text-xs">8 chunks done</span>
                 <button className="text-error-crimson hover:underline font-mono text-[10px] uppercase">Kick</button>
               </div>
               <div className="flex justify-between items-center text-sm border-b border-border-base/50 pb-2">
                 <span className="font-mono text-primary font-bold">NODE-112B</span>
                 <span className="text-secondary font-mono text-xs">2 chunks done</span>
                 <button className="text-error-crimson hover:underline font-mono text-[10px] uppercase">Kick</button>
               </div>
             </div>
          </div>
        )}

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full md:w-1/2 bg-[#0a0a0a] border border-[#333] rounded-sm flex flex-col overflow-hidden shadow-2xl">
        <div className="bg-[#1a1a1a] border-b border-[#333] px-4 py-2 flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-error-crimson"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-surface-tint"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-success-emerald"></div>
          </div>
          <span className="font-mono text-[10px] text-gray-400 uppercase tracking-widest ml-4">Live Orchestrator Feed</span>
        </div>
        
        <div className="p-4 flex-grow overflow-y-auto font-mono text-xs custom-scrollbar">
          {terminalLogs.map((log, idx) => {
            if (!log) return null;
            let color = "text-gray-300";
            if (log.includes("[SUCCESS]")) color = "text-success-emerald";
            if (log.includes("[WARNING]")) color = "text-amber-500";
            if (log.includes("[SYSTEM]")) color = "text-blue-400";
            if (log.includes("[INFO]")) color = "text-purple-400";
            
            return (
              <div key={idx} className="mb-1.5 flex gap-3">
                <span className="text-gray-600 select-none">{new Date().toISOString().substring(11, 19)}</span>
                <span className={color}>{log}</span>
              </div>
            );
          })}
          <div className="mt-2 text-gray-500 animate-pulse">_</div>
        </div>
      </div>

    </div>
  );
}
