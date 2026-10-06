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
    return nameMatch || idMatch;
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
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-4">
          <div className="bg-surface border border-border-base w-full max-w-sm rounded-[16px] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="border-b border-border-base px-6 py-4 flex justify-between items-center bg-surface-container">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-primary">lock</span>
                <h2 className="micro-label font-bold text-primary">Protected Task Access</h2>
              </div>
              <button onClick={() => setSelectedJob(null)} className="text-secondary hover:text-error-crimson p-1 rounded-[6px]">
                <span className="material-symbols-outlined text-[16px]">close</span>
              </button>
            </div>
            
            <form onSubmit={handleVerifyPassword} className="p-6 space-y-4">
              <div>
                <label className="micro-label text-secondary block mb-1.5">Cluster Passkey</label>
                <input 
                  autoFocus
                  required 
                  type="password" 
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[6px]" 
                  placeholder="Enter orchestrator passkey..." 
                />
                {passwordError && (
                  <p className="text-error-crimson text-[11px] font-mono mt-2">{passwordError}</p>
                )}
              </div>
              
              <div className="pt-3 border-t border-border-base flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setSelectedJob(null)} 
                  className="px-4 py-2 text-xs micro-label text-secondary hover:text-foreground hover:bg-surface-container transition-all rounded-[8px]"
                >
                  Cancel
                </button>
                <button 
                  disabled={isVerifying} 
                  type="submit" 
                  className="btn-interactive px-5 py-2 text-xs micro-label bg-primary text-on-primary font-bold rounded-[8px] border border-primary flex items-center gap-2"
                >
                  {isVerifying ? "Verifying..." : "Authenticate"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-2">
        <div>
          <h1 className="text-3xl font-bold title-tight text-primary mb-1">
            {poolFilter === "public" ? "Global Compute Pool" : "Private Cluster Gateway"}
          </h1>
          <p className="text-sm font-sans text-secondary">
            {poolFilter === "public" 
              ? "Discover and claim public compute workloads donated to the decentralized grid." 
              : "Isolated enterprise workloads partitioned into dedicated private cluster pools."}
          </p>
        </div>
        
        <div className="relative w-full md:w-80">
          <span className="material-symbols-outlined absolute left-3 top-2.5 text-secondary text-[16px]">search</span>
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface border border-border-base rounded-[8px] py-2 pl-9 pr-3 text-sm font-mono focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" 
            placeholder="Search Job ID or Alias..." 
          />
        </div>
      </div>

      {/* Pool Switcher Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border-base">
        <div className="flex items-center gap-2 bg-surface-container p-1 rounded-[10px] border border-border-base">
          <button
            onClick={() => setPoolFilter("public")}
            className={`flex items-center gap-2 px-3.5 py-1.5 micro-label rounded-[6px] transition-all ${
              poolFilter === "public"
                ? "bg-primary text-on-primary font-bold shadow-sm"
                : "text-secondary hover:text-primary hover:bg-surface"
            }`}
          >
            <span className="material-symbols-outlined text-[14px]">public</span>
            Global Pool (Public)
          </button>

          <button
            onClick={() => setPoolFilter("private")}
            className={`flex items-center gap-2 px-3.5 py-1.5 micro-label rounded-[6px] transition-all ${
              poolFilter === "private"
                ? "bg-primary text-on-primary font-bold shadow-sm"
                : "text-secondary hover:text-primary hover:bg-surface"
            }`}
          >
            <span className="material-symbols-outlined text-[14px]">lock</span>
            Private Clusters
          </button>
        </div>

        {poolFilter === "private" && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <span className="micro-label text-secondary whitespace-nowrap">Target Cluster:</span>
            <input
              type="text"
              value={clusterIdInput}
              onChange={(e) => setClusterIdInput(e.target.value)}
              placeholder="e.g. private_cluster_01"
              className="bg-surface border border-border-base rounded-[6px] px-3 py-1.5 font-mono text-xs text-primary focus:outline-none focus:border-primary w-full sm:w-60"
            />
          </div>
        )}
      </div>

      {/* Job Grid */}
      {filteredJobs.length === 0 ? (
        <div className="mt-8 text-center text-secondary font-mono text-xs p-12 border border-dashed border-border-base rounded-[16px] bg-surface/50">
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
              className="card-interactive cursor-pointer bg-surface border border-border-base rounded-[16px] p-5 hover:border-primary flex flex-col relative shadow-sm group"
            >
              <div className="flex justify-between items-start mb-3">
                <span className="ide-chip font-bold text-primary border-primary/30 group-hover:border-primary">
                  #{job.job_id.substring(0, 10)}
                </span>
                
                <div className="flex gap-2 items-center">
                  <span className="ide-chip text-[10px] text-secondary">
                    {job.pool_id || "public_pool"}
                  </span>
                  {job.requires_password && (
                    <span className="material-symbols-outlined text-secondary text-[14px]" title="Password Protected">lock</span>
                  )}
                  <span className="ide-chip border-success-emerald/30 text-success-emerald text-[10px] bg-success-emerald/5">
                    <span className="active-dot"></span>
                    ACTIVE
                  </span>
                </div>
              </div>
              
              <h3 className="font-sans font-bold text-base mb-1 text-foreground group-hover:text-primary transition-colors line-clamp-1">
                {job.job_name}
              </h3>
              <div className="mb-6">
                <span className="ide-chip text-[10px] uppercase text-secondary">
                  {job.job_type}
                </span>
              </div>
              
              <div className="mt-auto pt-4 border-t border-border-base/70 flex justify-between items-center text-xs font-mono text-secondary">
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
