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
        // Backend is offline, ignore gracefully instead of throwing console.error
        // which triggers Next.js red error overlay
        setJobs([]);
      }
    };
    fetchJobs();
    const interval = setInterval(fetchJobs, 2000);
    return () => clearInterval(interval);
  }, []);

  const filteredJobs = jobs.filter(job => {
    if (job?.status !== "processing") return false;

    // Check pool isolation:
    if (poolFilter === "public") {
      // Only show jobs meant for public_pool
      if (job?.pool_id && job.pool_id !== "public_pool") return false;
    } else {
      // In private cluster mode, only show jobs for the targeted cluster
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
        setPasswordError("Incorrect password. Access denied.");
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
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-surface border border-border-base w-full max-w-sm shadow-2xl rounded-sm">
            <div className="border-b border-border-base px-6 py-4 flex justify-between items-center bg-surface">
              <h2 className="font-mono text-sm font-bold text-primary uppercase tracking-wider flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">lock</span>
                Protected Task
              </h2>
              <button onClick={() => setSelectedJob(null)} className="text-secondary hover:text-error-crimson">
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
            </div>
            
            <form onSubmit={handleVerifyPassword} className="p-6 space-y-4">
              <div>
                <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Access Password</label>
                <input 
                  autoFocus
                  required 
                  type="password" 
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-sm" 
                  placeholder="Enter orchestrator pass..." 
                />
                {passwordError && (
                  <p className="text-error-crimson text-[10px] font-mono mt-2">{passwordError}</p>
                )}
              </div>
              
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setSelectedJob(null)} className="px-4 py-2 text-sm font-mono uppercase text-secondary hover:bg-surface-container transition-colors rounded-sm border border-transparent">Cancel</button>
                <button disabled={isVerifying} type="submit" className="px-6 py-2 text-sm font-mono uppercase bg-primary text-on-primary hover:opacity-90 transition-opacity rounded-sm border border-primary flex items-center gap-2">
                  {isVerifying ? "Verifying..." : "Enter Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-2xl font-bold font-sans text-primary mb-1">
            {poolFilter === "public" ? "Global Compute Pool" : "Private Cluster Gateway"}
          </h1>
          <p className="text-sm font-sans text-secondary">
            {poolFilter === "public" 
              ? "Search and join public compute tasks donated to the open grid." 
              : "Isolated enterprise tasks partitioned into dedicated private clusters."}
          </p>
        </div>
        
        <div className="relative w-full md:w-72">
          <span className="material-symbols-outlined absolute left-3 top-2 text-secondary text-[18px]">search</span>
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface border border-border-base rounded-sm py-2 pl-9 pr-3 text-sm font-mono focus:outline-none focus:border-primary" 
            placeholder="Search Job ID or Name..." 
          />
        </div>
      </div>

      {/* Pool Switcher Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-8 border-b border-border-base pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPoolFilter("public")}
            className={`flex items-center gap-2 px-3.5 py-1.5 font-mono text-xs uppercase rounded transition-colors ${
              poolFilter === "public"
                ? "bg-primary text-on-primary font-bold shadow-sm"
                : "text-secondary hover:text-primary hover:bg-surface-container"
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">public</span>
            Global Pool (Public)
          </button>

          <button
            onClick={() => setPoolFilter("private")}
            className={`flex items-center gap-2 px-3.5 py-1.5 font-mono text-xs uppercase rounded transition-colors ${
              poolFilter === "private"
                ? "bg-primary text-on-primary font-bold shadow-sm"
                : "text-secondary hover:text-primary hover:bg-surface-container"
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">lock</span>
            Private Clusters
          </button>
        </div>

        {poolFilter === "private" && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <span className="font-mono text-xs text-secondary uppercase whitespace-nowrap">Target Cluster:</span>
            <input
              type="text"
              value={clusterIdInput}
              onChange={(e) => setClusterIdInput(e.target.value)}
              placeholder="e.g. private_cluster_01"
              className="bg-surface border border-border-base rounded px-3 py-1 font-mono text-xs text-primary focus:outline-none focus:border-primary w-full sm:w-56"
            />
          </div>
        )}
      </div>

      {/* Job Grid */}
      {filteredJobs.length === 0 ? (
        <div className="mt-12 text-center text-secondary font-mono text-xs p-8 border border-dashed border-border-base rounded">
          {poolFilter === "public" ? (
            <p>No active public jobs found in the global pool.</p>
          ) : (
            <p>No active jobs found for cluster ID <span className="text-primary font-bold">"{clusterIdInput}"</span>. Ensure the cluster alias matches your target deployment.</p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {filteredJobs.map(job => (
            <div 
              key={job.job_id} 
              onClick={() => handleJobClick(job)}
              className="cursor-pointer bg-surface border border-border-base rounded-sm p-5 hover:border-primary transition-colors group flex flex-col relative"
            >
              <div className="flex justify-between items-start mb-4">
                <span className="font-mono text-sm font-bold text-primary px-2 py-1 bg-surface rounded">#{job.job_id.substring(0, 12)}</span>
                
                <div className="flex gap-2 items-center">
                  <span className="font-mono text-[10px] text-secondary border border-border-base px-2 py-0.5 rounded bg-surface-container">
                    {job.pool_id || "public_pool"}
                  </span>
                  {job.requires_password && (
                    <span className="material-symbols-outlined text-secondary text-[14px]" title="Password Required">lock</span>
                  )}
                  <span className="font-mono text-[10px] text-success-emerald uppercase tracking-wider bg-success-emerald/10 px-2 py-1 rounded">Open</span>
                </div>
              </div>
              <h3 className="font-sans font-bold text-base mb-1 text-primary pr-6">{job.job_name}</h3>
              <span className="font-mono text-xs text-secondary mb-6">{job.job_type}</span>
              
              <div className="mt-auto pt-4 border-t border-border-base flex justify-between items-center text-sm font-sans">
                <div className="flex items-center gap-1.5 text-secondary">
                  <span className="material-symbols-outlined text-[16px]">database</span>
                  {job.progress}%
                </div>
                <div className="flex items-center gap-1.5 text-secondary">
                  <span className="material-symbols-outlined text-[16px]">grid_on</span>
                  {job.total_chunks || 10} Chunks
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
