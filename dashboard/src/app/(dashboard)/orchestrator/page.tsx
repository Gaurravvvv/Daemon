"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function OrchestratorDashboard() {
  const router = useRouter();
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeJobs, setActiveJobs] = useState<any[]>([]);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/jobs");
        const data = await res.json();
        setActiveJobs(data.jobs || []);
      } catch (e) {
        // Backend offline, fallback gracefully
        setActiveJobs([]);
      }
    };
    fetchJobs();
    const interval = setInterval(fetchJobs, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateJob = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const formData = new FormData(e.currentTarget);
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/jobs/upload_and_submit", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      setShowSubmitModal(false);
      setIsSubmitting(false);
      
      if (data.job_id) {
        router.push(`/orchestrator/job/${data.job_id}`);
      }
    } catch (e) {
      alert("Failed to submit job. Please ensure the backend is running on port 8000.");
      setIsSubmitting(false);
    }
  };

  const handleDeleteJob = async (jobId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${jobId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        setActiveJobs(prev => prev.filter(j => j.job_id !== jobId));
      }
    } catch (e) {
      alert("Failed to delete job. Backend may be offline.");
    }
  };

  // Derived KPI metrics
  const processingCount = activeJobs.filter(j => j.status === 'processing').length;
  const completedCount = activeJobs.filter(j => j.status === 'completed').length;
  const totalChunks = activeJobs.reduce((acc, curr) => acc + (curr.total_chunks || 10), 0);

  return (
    <>
      {/* Submit Job Modal Overlay */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-4">
          <div className="bg-surface border border-border-base w-full max-w-lg rounded-[16px] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="border-b border-border-base px-6 py-4 flex justify-between items-center bg-surface-container">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">rocket_launch</span>
                <h2 className="micro-label font-bold text-primary">Deploy New Compute Task</h2>
              </div>
              <button 
                onClick={() => setShowSubmitModal(false)} 
                className="text-secondary hover:text-error-crimson p-1 rounded-[6px] transition-colors"
              >
                <span className="material-symbols-outlined text-[16px]">close</span>
              </button>
            </div>
            
            <form onSubmit={handleCreateJob} className="p-6 space-y-5">
              <div>
                <label className="micro-label text-secondary block mb-1.5">Job Alias / Identifier</label>
                <input 
                  required 
                  name="job_name" 
                  type="text" 
                  className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[6px] transition-all" 
                  placeholder="e.g. distributed_edge_detection_batch_01" 
                />
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Strategy Type</label>
                  <select name="job_type" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-[6px] cursor-pointer">
                    <option value="math">Math / Compute</option>
                    <option value="image">Image Processing</option>
                    <option value="crypto">Cryptography</option>
                  </select>
                </div>
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Target Pool</label>
                  <select name="pool_id" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-[6px] cursor-pointer">
                    <option value="public_pool">public_pool</option>
                    <option value="private_cluster_01">private_cluster_01</option>
                  </select>
                </div>
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Compute Mode</label>
                  <select name="compute_mode" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-[6px] cursor-pointer">
                    <option value="any">Any (Hybrid)</option>
                    <option value="gpu_only">GPU Only</option>
                    <option value="cpu_only">CPU Only</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="micro-label text-secondary block mb-1.5">Payload File (.ZIP dataset)</label>
                <input 
                  required 
                  name="file" 
                  type="file" 
                  className="w-full bg-surface border border-border-base px-3 py-2 text-xs font-mono file:mr-4 file:py-1 file:px-3 file:border file:border-border-base file:rounded-[6px] file:text-xs file:font-mono file:bg-surface-container file:text-primary hover:file:border-primary focus:outline-none cursor-pointer rounded-[6px]" 
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Split Count (Partitions)</label>
                  <input 
                    name="split_count" 
                    type="number" 
                    defaultValue="10" 
                    min="1" 
                    max="100" 
                    className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-mono focus:outline-none focus:border-primary rounded-[6px]" 
                  />
                </div>
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Access Password (Optional)</label>
                  <input 
                    name="password" 
                    type="password" 
                    placeholder="None (Public)" 
                    className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-[6px]" 
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-border-base flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setShowSubmitModal(false)} 
                  className="px-4 py-2 text-xs micro-label text-secondary hover:text-foreground hover:bg-surface-container transition-all rounded-[8px] border border-transparent"
                >
                  Cancel
                </button>
                <button 
                  disabled={isSubmitting} 
                  type="submit" 
                  className="btn-interactive px-5 py-2 text-xs micro-label bg-primary text-on-primary font-bold rounded-[8px] border border-primary flex items-center gap-2 shadow-sm"
                >
                  {isSubmitting ? (
                    <>Deploying <span className="material-symbols-outlined text-[14px] animate-spin">sync</span></>
                  ) : "Deploy to Grid"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold title-tight text-primary mb-1">Orchestrator Console</h1>
          <p className="text-sm font-sans text-secondary">Manage, schedule, and track distributed jobs dispatched to the edge compute grid.</p>
        </div>
        <button 
          onClick={() => setShowSubmitModal(true)} 
          className="btn-interactive px-4 py-2.5 bg-primary text-on-primary text-xs micro-label font-bold rounded-[8px] border border-primary flex items-center gap-2 shadow-sm"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
          Deploy New Job
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between">
          <span className="micro-label text-secondary">Active Processing</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="kpi-numeral text-3xl text-primary">{processingCount}</span>
            <span className="ide-chip border-success-emerald/30 text-success-emerald text-[10px]">RUNNING</span>
          </div>
        </div>

        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between">
          <span className="micro-label text-secondary">Completed Jobs</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="kpi-numeral text-3xl text-foreground">{completedCount}</span>
            <span className="ide-chip border-border-base text-secondary text-[10px]">HISTORICAL</span>
          </div>
        </div>

        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between">
          <span className="micro-label text-secondary">Total Task Chunks</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="kpi-numeral text-3xl text-secondary">{totalChunks}</span>
            <span className="ide-chip border-border-base text-secondary text-[10px]">PARTITIONS</span>
          </div>
        </div>

        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between">
          <span className="micro-label text-secondary">Queue Broker</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="kpi-numeral text-xl text-success-emerald">RabbitMQ</span>
            <div className="flex items-center gap-1.5 ide-chip border-success-emerald/30 text-success-emerald text-[10px]">
              <span className="active-dot"></span>
              LIVE
            </div>
          </div>
        </div>
      </div>

      {/* Main Jobs Table */}
      <section className="bg-surface border border-border-base rounded-[16px] overflow-hidden shadow-sm">
        <div className="px-margin-md py-3.5 border-b border-border-base bg-surface-container flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[16px]">list_alt</span>
            <h2 className="micro-label font-bold text-foreground">Dispatched Cluster Tasks</h2>
          </div>
          <span className="micro-label text-secondary text-[10px]">
            {activeJobs.length} {activeJobs.length === 1 ? 'Job' : 'Jobs'} Recorded
          </span>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-bg-subtle text-[11px] font-mono text-secondary uppercase tracking-[0.4px] border-b border-border-base">
                <th className="px-margin-md py-3 font-semibold">Job ID</th>
                <th className="px-margin-md py-3 font-semibold">Alias</th>
                <th className="px-margin-md py-3 font-semibold">Strategy</th>
                <th className="px-margin-md py-3 font-semibold">Status</th>
                <th className="px-margin-md py-3 font-semibold">Cluster Progress</th>
                <th className="px-margin-md py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm font-sans">
              {activeJobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-margin-md py-12 text-center text-secondary font-mono text-xs">
                    <span className="material-symbols-outlined text-3xl mb-2 text-secondary/40 block">inbox</span>
                    No active jobs in the queue. Deploy a new job above to begin compute.
                  </td>
                </tr>
              ) : (
                activeJobs.map((job) => (
                  <tr 
                    key={job.job_id} 
                    onClick={() => router.push(`/orchestrator/job/${job.job_id}`)}
                    className="cursor-pointer hover:bg-surface-container/60 transition-colors border-b border-border-base/60 last:border-0 group"
                  >
                    <td className="px-margin-md py-4">
                      <span className="ide-chip font-bold text-primary border-primary/30 group-hover:border-primary">
                        #{job.job_id.substring(0, 10)}
                      </span>
                    </td>
                    <td className="px-margin-md py-4 font-semibold text-foreground">{job.job_name}</td>
                    <td className="px-margin-md py-4">
                      <span className="ide-chip uppercase text-[10px]">
                        {job.job_type}
                      </span>
                    </td>
                    <td className="px-margin-md py-4">
                      <span className={`inline-flex items-center gap-1.5 font-mono text-xs ${job.status === 'processing' ? 'text-success-emerald' : 'text-secondary'}`}>
                        <span className={job.status === 'processing' ? 'active-dot' : 'w-1.5 h-1.5 rounded-full bg-border-base'}></span> 
                        {job.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-margin-md py-4 w-60">
                      <div className="flex items-center gap-3">
                        <div className="flex-grow bg-surface-container rounded-full h-2 relative overflow-hidden border border-border-base/50">
                          <div 
                            className={`rounded-full h-full transition-all duration-500 ${job.status === 'processing' ? 'bg-success-emerald' : 'bg-primary/50'}`} 
                            style={{ width: `${job.progress || 0}%` }}
                          ></div>
                        </div>
                        <span className="font-mono text-[11px] text-secondary font-medium w-9">{job.progress || 0}%</span>
                      </div>
                    </td>
                    <td className="px-margin-md py-4 text-right">
                      <div className="flex justify-end gap-2">
                        {(job.status === 'completed' || job.status === 'halted') && (
                          <button 
                            onClick={(e) => handleDeleteJob(job.job_id, e)}
                            className="px-2.5 py-1 text-[11px] font-mono border border-error-crimson/40 hover:bg-error-crimson hover:text-white text-error-crimson transition-all rounded-[6px] flex items-center justify-center"
                            title="Delete Job"
                          >
                            <span className="material-symbols-outlined text-[14px]">delete</span>
                          </button>
                        )}
                        <Link 
                          href={`/orchestrator/job/${job.job_id}`} 
                          className="btn-interactive px-3 py-1 flex items-center justify-center text-[11px] micro-label border border-border-base hover:border-primary text-secondary hover:text-primary transition-all rounded-[6px] bg-surface-container"
                        >
                          Inspect
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
