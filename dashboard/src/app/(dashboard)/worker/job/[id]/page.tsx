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

export default function WorkerJobDetails({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const [job, setJob] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [events, setEvents] = useState<EventLog[]>([]);
  const lastTimestampRef = useRef<string | null>(null);
  const terminalLogsRef = useRef<HTMLDivElement>(null);

  // Poll job status
  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}`);
        if (!res.ok) {
           if (res.status === 404) router.push("/worker");
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

  const dockerCommand = `docker run --rm --gpus all -e POOL_ID="${job?.pool_id || "public_pool"}" daemon-worker`;

  const copyCommand = () => {
    navigator.clipboard.writeText(dockerCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
    <div className="flex flex-col md:flex-row gap-6 md:h-[calc(100vh-140px)] md:max-h-[calc(100vh-140px)]">
      
      {/* Left Column: Details & Instructions */}
      <div className="w-full md:w-1/2 flex flex-col gap-5 overflow-y-auto custom-scrollbar md:h-full pr-1">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
          <div>
            <Link href="/worker" className="text-secondary hover:text-primary micro-label flex items-center gap-1.5 mb-3 transition-colors">
              <span className="material-symbols-outlined text-[15px]">arrow_back</span>
              Back to Global Pool
            </Link>
            <h1 className="text-2xl font-bold title-tight text-primary mb-1">{job?.job_name || "Compute Job"}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="ide-chip text-[10px] text-secondary">
                POOL: {job?.pool_id || "public_pool"}
              </span>
              <span className="ide-chip text-[10px] uppercase text-primary border-primary/30">
                {job?.job_type || "Compute"}
              </span>
            </div>
          </div>
          
          <button 
            onClick={copyCommand}
            className={`btn-interactive px-4 py-2 border micro-label rounded-[8px] flex items-center gap-2 transition-all shadow-sm ${
              copied 
                ? "bg-success-emerald text-on-primary border-success-emerald" 
                : "bg-primary text-on-primary border-primary hover:opacity-90 font-bold"
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{copied ? "check" : "content_copy"}</span>
            {copied ? "Copied Command!" : "Copy Docker Run"}
          </button>
        </div>

        {/* Task Details Card */}
        <div className="card-interactive bg-surface border border-border-base rounded-[16px] p-5 shadow-sm">
          <div className="flex items-center gap-2 border-b border-border-base pb-3 mb-4">
            <span className="material-symbols-outlined text-primary text-[16px]">tune</span>
            <h2 className="micro-label font-bold text-foreground">Task Specifications</h2>
          </div>

          <div className="space-y-4">
            <div>
              <span className="micro-label text-secondary block mb-1">Payload MinIO URI</span>
              <div className="ide-chip w-full justify-between py-1.5 px-3 break-all border-border-base bg-surface-container">
                <span className="truncate">{job?.raw_data_url || "Awaiting payload upload..."}</span>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary block mb-1">Progress</span>
                <span className="kpi-numeral text-xl text-primary">{job?.progress || 0}%</span>
              </div>
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary block mb-1">Status</span>
                <span className={`ide-chip mt-0.5 text-[10px] uppercase ${
                  job?.status === 'completed' ? 'border-success-emerald/40 text-success-emerald' :
                  job?.status === 'halted' ? 'border-error-crimson/40 text-error-crimson' :
                  'border-primary/40 text-primary'
                }`}>
                  {job?.status || "partitioning"}
                </span>
              </div>
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary block mb-1">Mode</span>
                <span className={`ide-chip mt-0.5 text-[10px] uppercase ${
                  job?.compute_mode === 'gpu_only' ? 'border-amber-400/40 text-amber-400' :
                  job?.compute_mode === 'cpu_only' ? 'border-blue-400/40 text-blue-400' :
                  'border-success-emerald/40 text-success-emerald'
                }`}>
                  {job?.compute_mode === 'gpu_only' ? 'GPU' :
                   job?.compute_mode === 'cpu_only' ? 'CPU' :
                   'Hybrid'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Onboarding Instructions */}
        <div className="bg-surface border border-border-base rounded-[16px] p-5 shadow-sm mt-auto">
          <div className="flex items-center gap-2 border-b border-border-base pb-3 mb-4">
            <span className="material-symbols-outlined text-primary text-[16px]">terminal</span>
            <h2 className="micro-label font-bold text-foreground">Worker Node Attachment</h2>
          </div>

          <ol className="space-y-4 font-sans text-sm text-secondary list-decimal list-inside">
            <li>
              <span className="font-semibold text-foreground">Ensure Docker Daemon is Running</span>
              <p className="pl-5 mt-1 text-xs">Verify Docker Desktop or Docker Engine is active with container virtualization support.</p>
            </li>
            <li>
              <span className="font-semibold text-foreground">Execute Worker Container</span>
              <div className="mt-2 ml-5 p-3 bg-surface-container border border-border-base rounded-[8px] font-mono text-[11px] text-primary break-all relative">
                {dockerCommand}
              </div>
              <p className="pl-5 mt-1.5 text-[11px] text-secondary font-mono">
                * To run on CPU-only machines, simply remove <code className="text-primary font-bold">--gpus all</code>.
              </p>
            </li>
            <li>
              <span className="font-semibold text-foreground">Real-time Stream Verification</span>
              <p className="pl-5 mt-1 text-xs">Your node will register, transmit heartbeats, and pull chunks automatically.</p>
            </li>
          </ol>
        </div>

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full md:w-1/2 h-[520px] md:h-full bg-surface border border-border-base rounded-[16px] flex flex-col overflow-hidden shadow-xl shrink-0">
        <div className="bg-surface-container border-b border-border-base px-4 py-3 flex items-center gap-3 shrink-0">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-error-crimson/80 border border-error-crimson"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-amber-400/80 border border-amber-400"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-success-emerald/80 border border-success-emerald"></div>
          </div>
          <span className="micro-label text-secondary ml-3">Live Worker Event Stream</span>
          <span className="ml-auto ide-chip text-[10px] text-secondary">{events.length} events</span>
        </div>
        
        <div ref={terminalLogsRef} className="p-4 flex-1 min-h-0 overflow-y-auto font-mono text-xs custom-scrollbar bg-bg-subtle">
          {events.length === 0 && (
            <div className="text-secondary/70 py-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-sm animate-spin">sync</span>
              Awaiting worker event packets...
            </div>
          )}
          {events.map((evt, idx) => {
            const time = new Date(evt.timestamp).toLocaleTimeString();
            return (
              <div key={idx} className="mb-2 flex items-start gap-2.5 leading-relaxed">
                <span className="text-secondary/60 select-none shrink-0 text-[11px] font-mono">[{time}]</span>
                <span className="ide-chip text-[10px] py-0 px-1.5 shrink-0 border-border-base">
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
