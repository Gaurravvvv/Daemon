"use client";

import React, { useState, useEffect, useRef, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface EventLog {
  timestamp: string;
  source: string;
  level: string;
  message: string;
  worker_id?: string;
}

export default function OrchestratorJobDetails({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const [job, setJob] = useState<any>(null);
  const [events, setEvents] = useState<EventLog[]>([]);
  const lastTimestampRef = useRef<string | null>(null);
  const terminalLogsRef = useRef<HTMLDivElement>(null);

  const handleHalt = async () => {
    if (!job) return;
    try {
      await fetch(`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/halt`, {
        method: "PUT",
      });
      setJob({ ...job, status: "halted" });
    } catch (e) {
      console.error("Failed to halt job", e);
    }
  };

  // Poll job status
  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}`);
        if (!res.ok) {
           if (res.status === 404) router.push("/orchestrator");
           return;
        }
        setJob(await res.json());
      } catch (e) { /* retry next interval */ }
    };
    fetchJob();
    const interval = setInterval(fetchJob, 3000);
    return () => clearInterval(interval);
  }, [resolvedParams.id, router]);

  // Poll real events from the API
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const url = lastTimestampRef.current
          ? `http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/events?after=${encodeURIComponent(lastTimestampRef.current)}`
          : `http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/events`;
        const res = await fetch(url);
        if (!res.ok) return;
        const data = await res.json();
        const newEvents: EventLog[] = data.events || [];
        if (newEvents.length > 0) {
          setEvents(prev => [...prev, ...newEvents]);
          lastTimestampRef.current = newEvents[newEvents.length - 1].timestamp;
        }
      } catch (e) { /* retry next interval */ }
    };
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, [resolvedParams.id]);

  // Auto-scroll terminal internally
  useEffect(() => {
    if (terminalLogsRef.current) {
      terminalLogsRef.current.scrollTop = terminalLogsRef.current.scrollHeight;
    }
  }, [events]);

  if (!job) {
    return (
      <div className="h-64 flex flex-col items-center justify-center gap-3">
        <span className="material-symbols-outlined text-4xl text-primary animate-spin">sync</span>
        <span className="micro-label text-secondary">Connecting to Orchestrator Node...</span>
      </div>
    );
  }

  const getLogColor = (level: string) => {
    switch (level) {
      case "SUCCESS": return "text-success-emerald";
      case "WARNING": return "text-amber-400";
      case "ERROR": return "text-error-crimson";
      case "SYSTEM": return "text-primary";
      case "INFO": return "text-secondary";
      default: return "text-foreground";
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-5 lg:gap-6 md:h-[calc(100vh-130px)] md:min-h-[500px]">
      
      {/* Left Column: Metrics & Controls */}
      <div className="w-full md:flex-1 min-w-0 flex flex-col gap-4 sm:gap-5 overflow-y-auto custom-scrollbar md:h-full pr-0 md:pr-1">
        
        {/* Header */}
        <div>
          <Link href="/orchestrator" className="text-secondary hover:text-primary micro-label inline-flex items-center gap-1.5 mb-2.5 transition-colors">
            <span className="material-symbols-outlined text-[15px]">arrow_back</span>
            Back to Jobs
          </Link>
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-1">
            <h1 className="text-xl sm:text-2xl font-bold title-tight text-primary">Job #{resolvedParams.id.substring(0, 14)}</h1>
            <span className={`ide-chip ${
              job.status === 'completed' ? 'border-success-emerald/40 text-success-emerald bg-success-emerald/5' :
              job.status === 'halted' ? 'border-error-crimson/40 text-error-crimson bg-error-crimson/5' :
              job.status === 'processing' ? 'border-primary/40 text-primary bg-primary/5' :
              'border-border-base text-secondary'
            }`}>
              <span className={job.status === 'processing' ? 'active-dot' : 'w-1.5 h-1.5 rounded-full bg-border-base'}></span>
              {job.status.toUpperCase()}
            </span>
          </div>
          <p className="text-xs sm:text-sm font-sans text-secondary truncate">{job.job_name || 'Unnamed Compute Job'}</p>
        </div>

        {/* Big Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="card-interactive bg-surface border border-border-base p-4 rounded-[12px] flex flex-col justify-between shadow-sm sm:col-span-2 min-h-[88px]">
            <div className="flex justify-between items-center mb-1">
              <span className="micro-label text-secondary">Cluster Progress</span>
              <span className="kpi-numeral text-2xl text-primary">{job?.progress || 0}%</span>
            </div>
            <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden border border-border-base/40 mt-1">
              <div 
                className="bg-success-emerald h-full transition-all duration-500 rounded-full" 
                style={{ width: `${job?.progress || 0}%` }}
              ></div>
            </div>
          </div>
          
          <div className="card-interactive bg-surface border border-border-base p-4 rounded-[12px] flex flex-col justify-between shadow-sm min-h-[88px]">
            <span className="micro-label text-secondary mb-1">Strategy Type</span>
            <span className="ide-chip mt-1 self-start uppercase font-bold text-primary">
              {job?.job_type || "Compute"}
            </span>
          </div>
          
          <div className="card-interactive bg-surface border border-border-base p-4 rounded-[12px] flex flex-col justify-between shadow-sm min-h-[88px]">
            <span className="micro-label text-secondary mb-1">Target Pool</span>
            <span className="ide-chip mt-1 self-start font-mono text-secondary truncate max-w-full">
              {job?.pool_id || "public_pool"}
            </span>
          </div>

          <div className="card-interactive bg-surface border border-border-base p-4 rounded-[12px] flex flex-col justify-between shadow-sm min-h-[88px]">
            <span className="micro-label text-secondary mb-1">Compute Mode</span>
            <span className={`ide-chip mt-1 self-start ${
              job?.compute_mode === 'gpu_only' ? 'border-amber-400/40 text-amber-400' :
              job?.compute_mode === 'cpu_only' ? 'border-blue-400/40 text-blue-400' :
              'border-success-emerald/40 text-success-emerald'
            }`}>
              {job?.compute_mode === 'gpu_only' ? 'GPU Only' :
               job?.compute_mode === 'cpu_only' ? 'CPU Only' :
               'Hybrid (Any)'}
            </span>
          </div>

          <div className="card-interactive bg-surface border border-border-base p-4 rounded-[12px] flex flex-col justify-between shadow-sm min-h-[88px]">
            <span className="micro-label text-secondary mb-1">Total Partitions</span>
            <span className="kpi-numeral text-xl text-foreground mt-1">
              {job?.total_chunks || 10} Chunks
            </span>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-surface border border-border-base rounded-[16px] overflow-hidden mt-auto shadow-sm">
          <div className="bg-surface-container border-b border-border-base px-4 py-3 flex justify-between items-center">
             <span className="micro-label text-foreground font-bold flex items-center gap-2">
               <span className="material-symbols-outlined text-[16px] text-primary">tune</span>
               Admin Orchestration Controls
             </span>
          </div>
          <div className="p-4 flex flex-wrap gap-3">
            <button 
              onClick={handleHalt}
              disabled={job.status === "halted" || job.status === "completed"}
              className="btn-interactive w-full sm:w-auto px-4 py-2 bg-error-crimson/10 text-error-crimson border border-error-crimson/30 hover:bg-error-crimson hover:text-white micro-label rounded-[8px] inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <span className="material-symbols-outlined text-[16px]">stop_circle</span>
              {job.status === "halted" ? "Job Halted" : "Halt Entire Job"}
            </button>
            {job.status === "completed" && (
              <a
                href={`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/download`}
                className="btn-interactive w-full sm:w-auto px-4 py-2 bg-success-emerald/10 text-success-emerald border border-success-emerald/30 hover:bg-success-emerald hover:text-on-primary micro-label rounded-[8px] inline-flex items-center justify-center gap-2 transition-all shadow-sm"
              >
                <span className="material-symbols-outlined text-[16px]">download</span>
                Download Output Artifacts
              </a>
            )}
          </div>
        </div>

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full md:flex-1 min-w-0 h-[420px] sm:h-[480px] md:h-full bg-surface border border-border-base rounded-[16px] flex flex-col overflow-hidden shadow-xl">
        <div className="bg-surface-container border-b border-border-base px-4 py-3 flex items-center gap-3 shrink-0">
          <div className="flex gap-1.5 shrink-0">
            <div className="w-2.5 h-2.5 rounded-full bg-error-crimson/80 border border-error-crimson"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-amber-400/80 border border-amber-400"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-success-emerald/80 border border-success-emerald"></div>
          </div>
          <span className="micro-label text-secondary ml-1 sm:ml-2 truncate">Live Orchestrator Event Stream</span>
          <span className="ml-auto ide-chip text-[10px] text-secondary shrink-0">{events.length} events</span>
        </div>
        
        <div ref={terminalLogsRef} className="p-3.5 sm:p-4 flex-1 min-h-0 overflow-y-auto font-mono text-xs custom-scrollbar bg-bg-subtle">
          {events.length === 0 && (
            <div className="text-secondary/70 py-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-sm animate-spin">sync</span>
              Awaiting worker event signals...
            </div>
          )}
          {events.map((evt, idx) => {
            const time = new Date(evt.timestamp).toLocaleTimeString();
            return (
              <div key={idx} className="mb-2 flex items-start gap-2 sm:gap-2.5 leading-relaxed text-[11px] sm:text-xs">
                <span className="text-secondary/60 select-none shrink-0 text-[10px] sm:text-[11px] font-mono">[{time}]</span>
                <span className="ide-chip text-[9px] sm:text-[10px] py-0 px-1.5 shrink-0 border-border-base">
                  {evt.source}
                </span>
                <span className={`${getLogColor(evt.level)} break-all`}>
                  {evt.message}
                </span>
              </div>
            );
          })}
          <div className="mt-2 text-primary font-bold animate-pulse">▋</div>
        </div>
      </div>

    </div>
  );
}
