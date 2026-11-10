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
  const [logSearch, setLogSearch] = useState("");
  const [levelFilter, setLevelFilter] = useState("ALL");
  const [copiedLogs, setCopiedLogs] = useState(false);
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

  const copyAllLogs = () => {
    const text = events.map(e => `[${new Date(e.timestamp).toISOString()}] [${e.source}] [${e.level}] ${e.message}`).join("\n");
    navigator.clipboard.writeText(text);
    setCopiedLogs(true);
    setTimeout(() => setCopiedLogs(false), 2000);
  };

  if (!job) {
    return (
      <div className="h-64 flex flex-col items-center justify-center gap-3">
        <span className="material-symbols-outlined text-4xl text-primary animate-spin">sync</span>
        <span className="micro-label text-secondary">Connecting to Orchestrator Node...</span>
      </div>
    );
  }

  const getLogColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case "SUCCESS": return "text-success-emerald";
      case "WARNING": return "text-amber-400";
      case "ERROR": return "text-error-crimson font-semibold";
      case "SYSTEM": return "text-primary";
      case "INFO": return "text-secondary";
      default: return "text-foreground";
    }
  };

  const formatStrategyName = (type: string) => {
    switch ((type || "").toLowerCase()) {
      case "csv_cleaning":
      case "csv":
      case "tabular":
      case "data_cleaning":
        return "CSV Dataset Cleaning";
      case "math":
      case "matrix":
        return "Matrix Compute";
      case "image":
        return "Image Processing";
      case "crypto":
        return "Cryptography";
      default:
        return type || "Compute";
    }
  };

  const filteredEvents = events.filter(e => {
    if (levelFilter !== "ALL" && e.level?.toUpperCase() !== levelFilter) return false;
    if (!logSearch.trim()) return true;
    const q = logSearch.toLowerCase();
    return (
      (e.message || "").toLowerCase().includes(q) ||
      (e.source || "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex flex-col lg:flex-row gap-5 lg:gap-6 flex-1 min-h-0 lg:h-[calc(100vh-125px)]" suppressHydrationWarning>
      
      {/* Left Column: Metrics & Controls */}
      <div className="w-full lg:w-[48%] flex flex-col gap-4 sm:gap-5 lg:h-full overflow-y-auto custom-scrollbar pr-0 lg:pr-2 min-h-0 shrink-0">
        
        {/* Header Breadcrumb & Status */}
        <div className="space-y-1 shrink-0">
          <Link href="/orchestrator" className="text-secondary hover:text-primary micro-label inline-flex items-center gap-1.5 transition-colors">
            <span className="material-symbols-outlined text-[15px]">arrow_back</span>
            Back to Dispatched Jobs
          </Link>
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <div className="flex items-center gap-2.5 min-w-0">
              <h1 className="text-xl sm:text-2xl font-bold title-tight text-primary truncate">
                Job #{resolvedParams.id.substring(0, 12)}
              </h1>
              <span className={`ide-chip ${
                job.status === 'completed' ? 'border-primary text-primary bg-primary/5' :
                job.status === 'halted' ? 'border-error-crimson text-error-crimson bg-error-crimson/5' :
                job.status === 'processing' ? 'border-success-emerald text-success-emerald bg-success-emerald/5' :
                'border-border-base text-secondary'
              }`}>
                <span className={job.status === 'processing' ? 'active-dot' : 'w-1.5 h-1.5 rounded-full bg-border-base'}></span>
                {job.status.toUpperCase()}
              </span>
            </div>
            
            {job.status === "completed" && (
              <a
                href={`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/download`}
                className="btn-interactive px-3 py-1.5 bg-primary text-on-primary text-xs micro-label font-bold rounded-[8px] inline-flex items-center gap-1.5 shadow-sm"
              >
                <span className="material-symbols-outlined text-[15px]">download</span>
                Download ZIP
              </a>
            )}
          </div>
          <p className="text-xs sm:text-sm font-sans text-secondary truncate">{job.job_name || 'Unnamed Compute Job'}</p>
        </div>

        {/* Big Metrics Grid */}
        <div className="flex flex-col gap-2.5 shrink-0">
          {/* Progress Card */}
          <div className="card-interactive bg-surface border border-border-base p-3.5 rounded-[12px] flex flex-col justify-between shadow-sm">
            <div className="flex justify-between items-center mb-1">
              <span className="micro-label text-secondary">Cluster Progress</span>
              <span className="kpi-numeral text-2xl text-primary">{job?.progress || 0}%</span>
            </div>
            <div className="w-full bg-surface-container h-2.5 rounded-full overflow-hidden border border-border-base/50 mt-1">
              <div 
                className={`h-full transition-all duration-500 rounded-full ${
                  job.status === 'processing' ? 'bg-success-emerald' : 
                  job.status === 'completed' ? 'bg-primary' :
                  'bg-primary/50'
                }`}
                style={{ width: `${job?.progress || 0}%` }}
              ></div>
            </div>
          </div>
          
          {/* 4 Metadata Cards in 1 Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="card-interactive bg-surface border border-border-base p-2.5 rounded-[10px] flex flex-col justify-between shadow-sm min-h-[72px]">
              <span className="micro-label text-secondary text-[10px] mb-1">Strategy</span>
              <span className="ide-chip self-start font-medium text-foreground text-[11px] truncate max-w-full">
                {formatStrategyName(job?.job_type)}
              </span>
            </div>
            
            <div className="card-interactive bg-surface border border-border-base p-2.5 rounded-[10px] flex flex-col justify-between shadow-sm min-h-[72px]">
              <span className="micro-label text-secondary text-[10px] mb-1">Target Pool</span>
              <span className="ide-chip self-start font-mono text-secondary truncate max-w-full text-[11px]">
                {job?.pool_id || "public_pool"}
              </span>
            </div>

            <div className="card-interactive bg-surface border border-border-base p-2.5 rounded-[10px] flex flex-col justify-between shadow-sm min-h-[72px]">
              <span className="micro-label text-secondary text-[10px] mb-1">Compute Mode</span>
              <span className={`ide-chip self-start text-[10px] ${
                job?.compute_mode === 'gpu_only' ? 'border-amber-400/40 text-amber-400' :
                job?.compute_mode === 'cpu_only' ? 'border-blue-400/40 text-blue-400' :
                'border-success-emerald/40 text-success-emerald'
              }`}>
                {job?.compute_mode === 'gpu_only' ? 'GPU' :
                 job?.compute_mode === 'cpu_only' ? 'CPU' :
                 'Hybrid'}
              </span>
            </div>

            <div className="card-interactive bg-surface border border-border-base p-2.5 rounded-[10px] flex flex-col justify-between shadow-sm min-h-[72px]">
              <span className="micro-label text-secondary text-[10px] mb-1">Partitions</span>
              <span className="kpi-numeral text-base text-foreground mt-0.5">
                {job?.completed_chunks || 0} / {job?.total_chunks || 10}
              </span>
            </div>
          </div>
        </div>

        {/* Dataset Cleaning Audit Card (if available) */}
        {job?.audit_summary && (
          <div className="bg-surface border border-border-base rounded-[16px] shadow-sm p-4 sm:p-5 space-y-3.5 shrink-0">
            <div className="flex items-center justify-between border-b border-border-base pb-3">
              <span className="micro-label font-bold text-primary flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">verified</span>
                Distributed Cleaning Audit Report
              </span>
              <span className="ide-chip text-[11px] font-bold text-primary border-primary/40 bg-primary/5">
                {job.audit_summary.retention_rate_pct}% RETAINED
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary text-[10px] block mb-1">Clean Rows</span>
                <span className="kpi-numeral text-lg text-primary">{job.audit_summary.total_clean_rows?.toLocaleString()}</span>
              </div>
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary text-[10px] block mb-1">Duplicates Purged</span>
                <span className="kpi-numeral text-lg text-error-crimson">{job.audit_summary.total_duplicates_removed?.toLocaleString()}</span>
              </div>
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary text-[10px] block mb-1">Nulls Cleaned</span>
                <span className="kpi-numeral text-lg text-amber-400">{job.audit_summary.total_null_cells_sanitized?.toLocaleString()}</span>
              </div>
              <div className="p-3 bg-surface-container rounded-[10px] border border-border-base">
                <span className="micro-label text-secondary text-[10px] block mb-1">PII Scrubbed</span>
                <span className="kpi-numeral text-lg text-success-emerald">{job.audit_summary.total_pii_entities_masked?.toLocaleString()}</span>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs font-mono text-secondary pt-1 border-t border-border-base/50">
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[14px]">speed</span>
                Throughput: {job.audit_summary.aggregate_cluster_throughput_rows_per_sec?.toLocaleString()} rows/s
              </span>
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[14px]">timer</span>
                Time: {job.audit_summary.total_cleaning_time_seconds}s
              </span>
            </div>
          </div>
        )}

        {/* Admin Controls */}
        <div className="bg-surface border border-border-base rounded-[16px] overflow-hidden shrink-0 shadow-sm">
          <div className="bg-surface-container border-b border-border-base px-4 py-3 flex justify-between items-center">
             <span className="micro-label text-foreground font-bold flex items-center gap-2">
               <span className="material-symbols-outlined text-[16px] text-primary">tune</span>
               Admin Orchestration Controls
             </span>
             <span className="text-[10px] font-mono text-secondary">Job ID: {resolvedParams.id}</span>
          </div>
          <div className="p-4 flex flex-wrap gap-3">
            <button 
              onClick={handleHalt}
              disabled={job.status === "halted" || job.status === "completed"}
              className="btn-interactive w-full sm:w-auto px-4 py-2 bg-error-crimson/10 text-error-crimson border border-error-crimson/30 hover:bg-error-crimson hover:text-white micro-label rounded-[8px] inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold"
            >
              <span className="material-symbols-outlined text-[16px]">stop_circle</span>
              {job.status === "halted" ? "Job Halted" : "Halt Entire Job"}
            </button>
            {job.status === "completed" && (
              <a
                href={`http://127.0.0.1:8000/api/v1/jobs/${resolvedParams.id}/download`}
                className="btn-interactive w-full sm:w-auto px-4 py-2 bg-primary text-on-primary border border-primary hover:opacity-95 micro-label rounded-[8px] inline-flex items-center justify-center gap-2 transition-all shadow-sm font-bold"
              >
                <span className="material-symbols-outlined text-[16px]">download</span>
                Download Output Deliverable
              </a>
            )}
          </div>
        </div>

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full lg:flex-1 min-w-0 h-[480px] lg:h-full bg-surface border border-border-base rounded-[16px] flex flex-col overflow-hidden shadow-xl shrink-0 lg:shrink">
        {/* Terminal Header */}
        <div className="bg-surface-container border-b border-border-base px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="flex gap-1.5 shrink-0">
              <div className="w-2.5 h-2.5 rounded-full bg-error-crimson/80 border border-error-crimson"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-amber-400/80 border border-amber-400"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-success-emerald/80 border border-success-emerald"></div>
            </div>
            <span className="micro-label text-foreground font-bold ml-1 truncate">Orchestrator Event Stream</span>
          </div>

          {/* Terminal Actions */}
          <div className="flex items-center gap-2 ml-auto">
            {/* Level Filter */}
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="h-7 bg-surface border border-border-base text-[10px] font-mono text-secondary rounded-[6px] px-2 focus:outline-none focus:border-primary cursor-pointer"
            >
              <option value="ALL">All Levels</option>
              <option value="INFO">Info</option>
              <option value="SUCCESS">Success</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
            </select>

            {/* Copy Logs */}
            <button
              onClick={copyAllLogs}
              className="h-7 px-2.5 text-[10px] font-mono border border-border-base hover:border-primary text-secondary hover:text-primary rounded-[6px] bg-surface inline-flex items-center gap-1 transition-colors"
              title="Copy All Logs"
            >
              <span className="material-symbols-outlined text-[12px]">{copiedLogs ? "check" : "content_copy"}</span>
              {copiedLogs ? "Copied" : "Copy"}
            </button>
            
            <span className="ide-chip text-[10px] text-secondary shrink-0">{filteredEvents.length} events</span>
          </div>
        </div>
        
        {/* Log Viewer Body */}
        <div ref={terminalLogsRef} className="p-3.5 sm:p-4 flex-1 min-h-0 overflow-y-auto font-mono text-xs custom-scrollbar bg-bg-subtle">
          {filteredEvents.length === 0 && (
            <div className="text-secondary/70 py-6 text-center flex flex-col items-center justify-center gap-2">
              <span className="material-symbols-outlined text-2xl text-secondary/40 animate-spin">sync</span>
              <span>Awaiting worker event signals from AMQP queue...</span>
            </div>
          )}
          {filteredEvents.map((evt, idx) => {
            const time = new Date(evt.timestamp).toLocaleTimeString();
            return (
              <div key={idx} className="mb-1.5 flex items-start gap-2 leading-relaxed text-[11px] sm:text-xs hover:bg-surface-container/30 px-1 rounded transition-colors">
                <span className="text-secondary/60 select-none shrink-0 font-mono text-[10px]">[{time}]</span>
                <span className="ide-chip text-[9px] py-0 px-1.5 shrink-0 border-border-base/70">
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
