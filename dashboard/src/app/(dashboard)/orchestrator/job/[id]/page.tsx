"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function OrchestratorJobDetails({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const [job, setJob] = useState<any>(null);
  const [showWorkers, setShowWorkers] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    "[SYSTEM] Fetching live job metadata from orchestrator...",
  ]);

  const handleHalt = async () => {
    if (!job) return;
    try {
      await fetch(`http://localhost:8000/api/v1/jobs/${resolvedParams.id}/halt`, {
        method: "PUT",
      });
      setJob({ ...job, status: "halted" });
    } catch (e) {
      console.error("Failed to halt job", e);
    }
  };

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/jobs/${resolvedParams.id}`);
        if (!res.ok) {
           if (res.status === 404) router.push("/orchestrator");
           return;
        }
        const data = await res.json();
        setJob(data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchJob();
    const interval = setInterval(fetchJob, 3000);
    return () => clearInterval(interval);
  }, [resolvedParams.id, router]);

  // Dynamic logs based on actual job state
  useEffect(() => {
    if (job) {
      setTerminalLogs(prev => {
        const newLogs = [...prev];
        const statusMsg = `[INFO] Job ${job.job_id} status updated to: ${job.status.toUpperCase()}`;
        if (!newLogs.includes(statusMsg)) {
          newLogs.push(statusMsg);
        }
        
        const progressMsg = `[PROGRESS] Grid progress: ${job.progress}% completed`;
        // Only push progress if it's new
        if (job.progress > 0 && !newLogs.includes(progressMsg)) {
          newLogs.push(progressMsg);
        }
        return newLogs;
      });
    }
  }, [job?.status, job?.progress]);

  if (!job) {
    return (
      <div className="h-full flex items-center justify-center">
        <span className="material-symbols-outlined text-4xl text-primary animate-spin">sync</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col md:flex-row gap-6 min-h-[calc(100vh-140px)] md:h-[calc(100vh-140px)]">
      
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
            <span className="text-3xl font-bold font-sans text-primary">{job?.progress || 0}<span className="text-lg text-secondary">%</span></span>
            <div className="w-full bg-surface-container h-1 mt-2">
              <div className="bg-success-emerald h-1 transition-all duration-500" style={{ width: `${job?.progress || 0}%` }}></div>
            </div>
          </div>
          
          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Job Alias</span>
            <span className="text-xl font-bold font-sans text-primary mt-1">{job?.job_name || "Unknown"}</span>
          </div>
          
          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Strategy Type</span>
            <span className="text-xl font-bold font-sans text-primary mt-1">{job?.job_type || "Compute"}</span>
          </div>
          
          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Target Pool</span>
            <span className="text-xl font-bold font-sans text-primary mt-1">{job?.pool_id || "public_pool"}</span>
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
            <button 
              onClick={handleHalt}
              disabled={job.status === "halted" || job.status === "completed"}
              className="px-4 py-2 bg-error-crimson/10 text-error-crimson border border-error-crimson/30 hover:bg-error-crimson hover:text-on-error transition-colors font-mono text-xs uppercase rounded-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[16px]">stop_circle</span>
              {job.status === "halted" ? "Halted" : "Halt Entire Task"}
            </button>
          </div>
        </div>

        {/* View Workers Panel (Toggled) */}
        {showWorkers && (
          <div className="bg-surface border border-border-base rounded-sm p-4 animate-in fade-in slide-in-from-top-4">
             <h3 className="font-mono text-xs uppercase text-secondary mb-3">Active Node Roster</h3>
             <div className="space-y-2">
               <div className="flex justify-center items-center text-sm pb-2">
                 <span className="text-secondary font-mono text-xs text-center">
                   Node Roster hidden. <br/>
                   <span className="opacity-70 mt-1 block">(Workers operate securely via RabbitMQ pull mechanism without direct IP exposure)</span>
                 </span>
               </div>
             </div>
          </div>
        )}

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full md:w-1/2 min-h-[400px] md:min-h-0 bg-[#0a0a0a] border border-[#333] rounded-sm flex flex-col overflow-hidden shadow-2xl">
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
