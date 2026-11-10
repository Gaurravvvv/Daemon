"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function WorkerDashboard() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [jobs, setJobs] = useState<any[]>([]);
  
  const [poolFilter, setPoolFilter] = useState<"public" | "private">("public");
  const [clusterIdInput, setClusterIdInput] = useState("private_cluster_01");
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [passwordInput, setPasswordInput] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/jobs");
        const data = await res.json();
        setJobs(data.jobs || []);
      } catch (e) {
        setJobs([]);
      }
    };
    fetchJobs();
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, []);

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

  const filteredJobs = jobs.filter(job => {
    if (job?.status !== "processing") return false;

    // Check pool isolation:
    if (poolFilter === "public") {
      if (job?.pool_id && job.pool_id !== "public_pool") return false;
    } else {
      if (!clusterIdInput.trim()) return false;
      if (job?.pool_id?.toLowerCase() !== clusterIdInput.trim().toLowerCase()) return false;
    }

    const nameMatch = (job?.job_name?.toLowerCase() || "").includes(searchQuery.toLowerCase());
    const idMatch = (job?.job_id?.toLowerCase() || "").includes(searchQuery.toLowerCase());
    const typeMatch = (job?.job_type?.toLowerCase() || "").includes(searchQuery.toLowerCase());
    return nameMatch || idMatch || typeMatch;
  });

  const handleJobClick = (job: any) => {
    if (job.requires_password) {
      setSelectedJob(job);
      setPasswordInput("");
      setPasswordError("");
    } else {
      router.push(`/worker/job/${job.job_id}`);
    }
  };

  const handleVerifyPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJob) return;
    
    setIsVerifying(true);
    setPasswordError("");
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${selectedJob.job_id}/verify_password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: passwordInput })
      });
      
      if (res.ok) {
        router.push(`/worker/job/${selectedJob.job_id}`);
      } else {
        setPasswordError("Incorrect passkey. Access denied.");
        setIsVerifying(false);
      }
    } catch (e) {
      setPasswordError("Verification failed. Please try again.");
      setIsVerifying(false);
    }
  };

  return (
    <>
      {/* Password Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-3 sm:p-4">
          <div className="bg-surface border border-border-base w-full max-w-sm max-h-[92vh] flex flex-col rounded-[16px] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="border-b border-border-base px-5 py-4 flex justify-between items-center bg-surface-container shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-[8px] bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[18px]">lock</span>
                </div>
                <div>
                  <h2 className="micro-label font-bold text-foreground">Protected Cluster Task</h2>
                  <p className="font-sans text-[11px] text-secondary">Passkey required to join</p>
                </div>
              </div>
              <button 
                type="button"
                onClick={() => setSelectedJob(null)} 
                className="text-secondary hover:text-foreground p-1.5 rounded-[6px] hover:bg-surface transition-colors inline-flex items-center justify-center"
                title="Close"
              >
                <span className="material-symbols-outlined text-[16px]">close</span>
              </button>
            </div>
            
            <form onSubmit={handleVerifyPassword} className="p-5 space-y-4 overflow-y-auto custom-scrollbar flex-1">
              <div>
                <label className="micro-label text-secondary block mb-1.5">Cluster Passkey</label>
                <input 
                  autoFocus
                  required 
                  type="password" 
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-sans text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px] transition-all placeholder:text-secondary/50" 
                  placeholder="Enter orchestrator passkey..." 
                />
                {passwordError && (
                  <p className="text-error-crimson text-[11px] font-mono mt-2">{passwordError}</p>
                )}
              </div>
              
              <div className="pt-3 border-t border-border-base flex justify-end gap-2.5 shrink-0">
                <button 
                  type="button" 
                  onClick={() => setSelectedJob(null)} 
                  className="px-3.5 py-1.5 text-xs micro-label text-secondary hover:text-foreground hover:bg-surface-container transition-all rounded-[6px]"
                >
                  Cancel
                </button>
                <button 
                  disabled={isVerifying} 
                  type="submit" 
                  className="btn-interactive px-4 py-1.5 text-xs micro-label bg-primary text-on-primary font-bold rounded-[6px] border border-primary inline-flex items-center justify-center gap-1.5 transition-all shadow-sm"
                >
                  {isVerifying ? "Verifying..." : "Authenticate"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-3 sm:gap-4 mb-2">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-bold title-tight text-primary">
            {poolFilter === "public" ? "Global Compute Pool" : "Private Cluster Gateway"}
          </h1>
          <p className="text-xs sm:text-sm font-sans text-secondary max-w-2xl">
            {poolFilter === "public" 
              ? "Discover and claim public compute workloads donated to the decentralized grid." 
              : "Isolated enterprise workloads partitioned into dedicated private cluster pools."}
          </p>
        </div>
        
        <div className="relative w-full md:w-80 shrink-0">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-secondary text-[16px] pointer-events-none">search</span>
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-10 bg-surface border border-border-base rounded-[8px] pl-9 pr-8 text-xs sm:text-sm font-mono text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-secondary/50" 
            placeholder="Search Job ID or Alias..." 
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-secondary hover:text-foreground"
            >
              <span className="material-symbols-outlined text-[14px]">close</span>
            </button>
          )}
        </div>
      </div>

      {/* Pool Switcher Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-border-base">
        <div className="flex items-center gap-1.5 bg-surface-container p-1 rounded-[10px] border border-border-base">
          <button
            onClick={() => setPoolFilter("public")}
            className={`flex items-center gap-2 px-3 sm:px-3.5 py-1.5 micro-label rounded-[6px] transition-all ${
              poolFilter === "public"
                ? "bg-primary text-on-primary font-bold shadow-xs"
                : "text-secondary hover:text-primary hover:bg-surface"
            }`}
          >
            <span className="material-symbols-outlined text-[15px]">public</span>
            Global Pool (Public)
          </button>

          <button
            onClick={() => setPoolFilter("private")}
            className={`flex items-center gap-2 px-3 sm:px-3.5 py-1.5 micro-label rounded-[6px] transition-all ${
              poolFilter === "private"
                ? "bg-primary text-on-primary font-bold shadow-xs"
                : "text-secondary hover:text-primary hover:bg-surface"
            }`}
          >
            <span className="material-symbols-outlined text-[15px]">lock</span>
            Private Clusters
          </button>
        </div>

        {poolFilter === "private" && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <span className="micro-label text-secondary whitespace-nowrap shrink-0">Target Cluster:</span>
            <input
              type="text"
              value={clusterIdInput}
              onChange={(e) => setClusterIdInput(e.target.value)}
              placeholder="e.g. private_cluster_01"
              className="bg-surface border border-border-base rounded-[8px] h-9 px-3 font-mono text-xs text-foreground focus:outline-none focus:border-primary w-full sm:w-60 min-w-0"
            />
          </div>
        )}
      </div>

      {/* Job Grid */}
      {filteredJobs.length === 0 ? (
        <div className="mt-8 text-center text-secondary font-mono text-xs p-8 sm:p-12 border border-dashed border-border-base rounded-[16px] bg-surface/50">
          <span className="material-symbols-outlined text-4xl mb-2 text-secondary/40 block">cloud_sync</span>
          {poolFilter === "public" ? (
            <p>No active public jobs found in the global pool. Waiting for orchestrator dispatches...</p>
          ) : (
            <p>No active jobs found for cluster <span className="text-primary font-bold">"{clusterIdInput}"</span>. Ensure worker pool configuration matches target.</p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredJobs.map(job => (
            <div 
              key={job.job_id} 
              onClick={() => handleJobClick(job)}
              className="card-interactive cursor-pointer bg-surface border border-border-base rounded-[16px] p-4 sm:p-5 hover:border-primary flex flex-col relative shadow-sm group transition-all"
            >
              <div className="flex justify-between items-start gap-2 mb-3">
                <span className="ide-chip font-bold text-primary border-primary/30 group-hover:border-primary shrink-0 truncate max-w-[130px]">
                  #{job.job_id.substring(0, 10)}
                </span>
                
                <div className="flex flex-wrap gap-1.5 items-center justify-end">
                  <span className="ide-chip text-[10px] text-secondary truncate max-w-[110px]">
                    {job.pool_id || "public_pool"}
                  </span>
                  {job.requires_password && (
                    <span className="material-symbols-outlined text-secondary text-[14px] shrink-0" title="Password Protected">lock</span>
                  )}
                  <span className="ide-chip border-success-emerald/30 text-success-emerald text-[10px] bg-success-emerald/5 shrink-0">
                    <span className="active-dot"></span>
                    ACTIVE
                  </span>
                </div>
              </div>
              
              <h3 className="font-sans font-bold text-base mb-1 text-foreground group-hover:text-primary transition-colors line-clamp-1">
                {job.job_name}
              </h3>
              <div className="mb-4">
                <span className="ide-chip text-[10px] text-secondary">
                  {formatStrategyName(job.job_type)}
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-surface-container rounded-full h-1.5 overflow-hidden border border-border-base/40 mb-4">
                <div 
                  className="bg-success-emerald h-full rounded-full transition-all duration-300" 
                  style={{ width: `${job.progress || 0}%` }}
                ></div>
              </div>
              
              <div className="mt-auto pt-3 border-t border-border-base/70 flex flex-wrap justify-between items-center gap-2 text-xs font-mono text-secondary">
                <div className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px] text-primary">data_usage</span>
                  <span>{job.progress || 0}% Complete</span>
                </div>
                <div className="flex items-center gap-1.5 ide-chip text-[10px]">
                  <span className="material-symbols-outlined text-[14px]">grid_view</span>
                  <span>{job.total_chunks || 10} Chunks</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
