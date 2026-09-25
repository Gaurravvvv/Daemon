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

  // Auto-scroll terminal internally (prevents page expansion)
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
      case "WARNING": return "text-amber-500";
      case "ERROR": return "text-error-crimson";
      case "SYSTEM": return "text-blue-400";
      case "INFO": return "text-purple-400";
      default: return "text-gray-300";
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 md:h-[calc(100vh-140px)] md:max-h-[calc(100vh-140px)]">
      
      {/* Left Column: Details & Instructions */}
      <div className="w-full md:w-1/2 flex flex-col gap-6 overflow-y-auto custom-scrollbar md:h-full pr-1">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 sm:gap-0">
          <div>
            <Link href="/worker" className="text-secondary hover:text-primary font-mono text-xs uppercase flex items-center gap-1 mb-4">
              <span className="material-symbols-outlined text-[14px]">arrow_back</span>
              Back to Global Pool
            </Link>
            <h1 className="text-2xl font-bold font-sans text-primary mb-1">{job?.job_name || "Unknown Job"}</h1>
            <p className="font-mono text-xs text-secondary">
              Pool: <span className="text-primary">{job?.pool_id || "public_pool"}</span> • Type: <span className="text-primary">{job?.job_type || "Compute"}</span>
            </p>
          </div>
          
          <button 
            onClick={copyCommand}
            className={`px-4 py-2 border font-mono text-xs uppercase rounded-sm flex items-center gap-2 transition-all ${
              copied ? "bg-success-emerald text-on-primary border-success-emerald" : "bg-primary text-on-primary border-primary hover:opacity-90"
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{copied ? "check" : "content_copy"}</span>
            {copied ? "Copied!" : "Copy Docker Command"}
          </button>
        </div>

        {/* Task Details Card */}
        <div className="bg-surface border border-border-base rounded-sm p-6">
          <h2 className="font-mono text-sm font-bold text-primary uppercase mb-4 border-b border-border-base pb-2">Payload Specifications</h2>
          <div className="space-y-4">
            <div>
              <span className="font-mono text-[10px] text-secondary uppercase tracking-widest block mb-1">Raw Data URI</span>
              <span className="font-sans font-medium text-sm break-all">{job?.raw_data_url || "Waiting for upload..."}</span>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <span className="font-mono text-[10px] text-secondary uppercase tracking-widest block mb-1">Global Progress</span>
                <span className="font-sans font-medium text-sm text-primary">{job?.progress || 0}%</span>
              </div>
              <div>
                <span className="font-mono text-[10px] text-secondary uppercase tracking-widest block mb-1">Status</span>
                <span className={`font-sans font-medium text-sm uppercase ${
                  job?.status === 'completed' ? 'text-success-emerald' :
                  job?.status === 'halted' ? 'text-error-crimson' :
                  'text-blue-400'
                }`}>{job?.status || "partitioning"}</span>
              </div>
              <div>
                <span className="font-mono text-[10px] text-secondary uppercase tracking-widest block mb-1">Compute Mode</span>
                <span className={`font-sans font-medium text-sm uppercase ${
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
          </div>
        </div>

        {/* Onboarding Instructions */}
        <div className="bg-surface border border-border-base rounded-sm p-6 mt-auto">
          <h2 className="font-mono text-sm font-bold text-primary uppercase mb-4 border-b border-border-base pb-2">How to Help Compute</h2>
          <ol className="space-y-4 list-decimal list-inside font-sans text-sm text-secondary">
            <li>
              <span className="font-medium text-primary">Start Docker Desktop</span>
              <p className="pl-4 mt-1">Ensure Docker is running with GPU support enabled (NVIDIA Container Toolkit).</p>
            </li>
            <li>
              <span className="font-medium text-primary">The Command</span>
              <div className="mt-2 ml-4 p-3 bg-surface-container border border-border-base rounded-sm font-mono text-[11px] text-primary break-all relative">
                {dockerCommand}
              </div>
              <p className="pl-4 mt-2 text-[10px] text-secondary font-mono">Note: First run downloads ~2GB GPU runtime (cached after first pull). No GPU? Remove --gpus all to run in CPU mode.</p>
            </li>
            <li>
              <span className="font-medium text-primary">Run the command</span>
              <p className="pl-4 mt-1">Copy and run this command in your terminal to instantly connect your node.</p>
            </li>
          </ol>
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
          <span className="font-mono text-[10px] text-gray-400 uppercase tracking-widest ml-4">Live Worker Feed</span>
          <span className="ml-auto font-mono text-[10px] text-gray-600">{events.length} events</span>
        </div>
        
        <div ref={terminalLogsRef} className="p-4 flex-1 min-h-0 overflow-y-auto font-mono text-xs custom-scrollbar">
          {events.length === 0 && (
            <div className="text-gray-500 mb-2">Waiting for worker events...</div>
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
