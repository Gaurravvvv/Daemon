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
  const [showWorkers, setShowWorkers] = useState(false);
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

  // Auto-scroll terminal internally (prevents page expansion)
  useEffect(() => {
    if (terminalLogsRef.current) {
      terminalLogsRef.current.scrollTop = terminalLogsRef.current.scrollHeight;
    }
  }, [events]);

  if (!job) {
    return (
      <div className="h-full flex items-center justify-center">
        <span className="material-symbols-outlined text-4xl text-primary animate-spin">sync</span>
      </div>
    );
  }

  const getLogColor = (level: string) => {
    switch (level) {
      case "SUCCESS": return "text-success-emerald";
      case "WARNING": return "text-amber-500";
      case "ERROR": return "text-error-crimson";
      case "SYSTEM": return "text-blue-400";
      case "INFO": return "text-purple-400";
      default: return "text-gray-300";
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 md:h-[calc(100vh-140px)] md:max-h-[calc(100vh-140px)]">
      
      {/* Left Column: Metrics & Controls */}
      <div className="w-full md:w-1/2 flex flex-col gap-6 overflow-y-auto custom-scrollbar md:h-full pr-1">
        
        {/* Header */}
        <div>
          <Link href="/orchestrator" className="text-secondary hover:text-primary font-mono text-xs uppercase flex items-center gap-1 mb-4">
            <span className="material-symbols-outlined text-[14px]">arrow_back</span>
            Back to Jobs
          </Link>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold font-sans text-primary">Job #{resolvedParams.id}</h1>
            <span className={`px-2 py-0.5 rounded text-xs font-mono uppercase border ${
              job.status === 'completed' ? 'bg-success-emerald/10 text-success-emerald border-success-emerald/20' :
              job.status === 'halted' ? 'bg-error-crimson/10 text-error-crimson border-error-crimson/20' :
              job.status === 'processing' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
              'bg-surface-tint/10 text-surface-tint border-surface-tint/20'
            }`}>{job.status}</span>
          </div>
          <p className="text-sm font-mono text-secondary">{job.job_name || 'Unnamed Job'}</p>
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

          <div className="bg-surface border border-border-base p-4 rounded-sm flex flex-col">
            <span className="font-mono text-[10px] text-secondary uppercase tracking-widest mb-1">Compute Mode</span>
            <span className={`text-xl font-bold font-sans mt-1 ${
              job?.compute_mode === 'gpu_only' ? 'text-amber-400' :
              job?.compute_mode === 'cpu_only' ? 'text-blue-400' :
              'text-success-emerald'
            }`}>
              {job?.compute_mode === 'gpu_only' ? 'GPU Only' :
               job?.compute_mode === 'cpu_only' ? 'CPU Only' :
               'Hybrid'}
            </span>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-surface border border-border-base rounded-sm overflow-hidden mt-auto">
          <div className="bg-surface border-b border-border-base px-4 py-3 flex justify-between items-center">
             <span className="font-mono text-xs uppercase text-primary font-bold">Admin Controls</span>
          </div>
          <div className="p-4 flex flex-wrap gap-3">
            <button 
              onClick={handleHalt}
              disabled={job.status === "halted" || job.status === "completed"}
              className="px-4 py-2 bg-error-crimson/10 text-error-crimson border border-error-crimson/30 hover:bg-error-crimson hover:text-on-error transition-colors font-mono text-xs uppercase rounded-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[16px]">stop_circle</span>
              {job.status === "halted" ? "Halted" : "Halt Entire Task"}
            </button>
            {job.status === "completed" && (
              <a
                href={`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/download`}
                className="px-4 py-2 bg-success-emerald/10 text-success-emerald border border-success-emerald/30 hover:bg-success-emerald hover:text-on-primary transition-colors font-mono text-xs uppercase rounded-sm flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[16px]">download</span>
                Download Results
              </a>
            )}
          </div>
        </div>

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full md:w-1/2 h-[520px] md:h-full bg-[#0a0a0a] border border-[#333] rounded-sm flex flex-col overflow-hidden shadow-2xl shrink-0">
        <div className="bg-[#1a1a1a] border-b border-[#333] px-4 py-2.5 flex items-center gap-3 shrink-0">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-error-crimson"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-surface-tint"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-success-emerald"></div>
          </div>
          <span className="font-mono text-[10px] text-gray-400 uppercase tracking-widest ml-4">Live Orchestrator Feed</span>
          <span className="ml-auto font-mono text-[10px] text-gray-600">{events.length} events</span>
        </div>
        
        <div ref={terminalLogsRef} className="p-4 flex-1 min-h-0 overflow-y-auto font-mono text-xs custom-scrollbar">
          {events.length === 0 && (
            <div className="text-gray-500 mb-2">Waiting for events...</div>
          )}
          {events.map((evt, idx) => {
            const time = new Date(evt.timestamp).toLocaleTimeString();
            return (
              <div key={idx} className="mb-1.5 flex gap-3">
                <span className="text-gray-600 select-none shrink-0">{time}</span>
                <span className={`${getLogColor(evt.level)} break-all`}>
                  [{evt.source}] {evt.message}
                </span>
              </div>
            );
          })}
          <div className="mt-2 text-gray-500 animate-pulse">_</div>
        </div>
      </div>

    </div>
  );
}
