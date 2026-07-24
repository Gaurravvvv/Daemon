"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function WorkerJobDetails({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const [job, setJob] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    "[SYSTEM] Fetching live job metadata from orchestrator...",
  ]);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/jobs/${resolvedParams.id}`);
        if (!res.ok) {
           if (res.status === 404) router.push("/worker");
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

  useEffect(() => {
    if (job) {
      setTerminalLogs(prev => {
        const newLogs = [...prev];
        const statusMsg = `[INFO] Job ${resolvedParams.id} state updated to: ${job.status.toUpperCase()}`;
        if (!newLogs.includes(statusMsg)) {
          newLogs.push(statusMsg);
        }
        
        const progressMsg = `[PROGRESS] Grid progress: ${job.progress || 0}% completed`;
        // Only push progress if it's new
        if (job.progress > 0 && !newLogs.includes(progressMsg)) {
          newLogs.push(progressMsg);
        }
        return newLogs;
      });
    }
  }, [job?.status, job?.progress, resolvedParams.id]);

  const dockerCommand = `docker run -e ORCHESTRATOR_URL="http://host.docker.internal:8000" -e RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/" -e MINIO_URL="http://host.docker.internal:9000" -e POOL_ID="${job?.pool_id || "public_pool"}" daemon-worker`;

  const copyCommand = () => {
    navigator.clipboard.writeText(dockerCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 min-h-[calc(100vh-140px)]">
      
      {/* Left Column: Details & Instructions */}
      <div className="w-full md:w-1/2 flex flex-col gap-6">
        
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
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-mono text-[10px] text-secondary uppercase tracking-widest block mb-1">Global Progress</span>
                <span className="font-sans font-medium text-sm text-primary">{job?.progress || 0}%</span>
              </div>
              <div>
                <span className="font-mono text-[10px] text-secondary uppercase tracking-widest block mb-1">Status</span>
                <span className="font-sans font-medium text-sm text-success-emerald uppercase">{job?.status || "partitioning"}</span>
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
              <p className="pl-4 mt-1">Ensure your Docker engine is running on your machine.</p>
            </li>
            <li>
              <span className="font-medium text-primary">The Command</span>
              <div className="mt-2 ml-4 p-3 bg-surface-container border border-border-base rounded-sm font-mono text-[11px] text-primary break-all relative">
                {dockerCommand}
              </div>
            </li>
            <li>
              <span className="font-medium text-primary">Run the command</span>
              <p className="pl-4 mt-1">Copy and run this command in your terminal to instantly connect your node.</p>
            </li>
          </ol>
        </div>

      </div>

      {/* Right Column: Live Terminal Feed */}
      <div className="w-full md:w-1/2 min-h-[400px] md:min-h-0 bg-[#0a0a0a] border border-[#333] rounded-sm flex flex-col overflow-hidden shadow-2xl">
        <div className="bg-[#1a1a1a] border-b border-[#333] px-4 py-2 flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-error-crimson"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-surface-tint"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-success-emerald"></div>
          </div>
          <span className="font-mono text-[10px] text-gray-400 uppercase tracking-widest ml-4">My Local Node Feed</span>
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
