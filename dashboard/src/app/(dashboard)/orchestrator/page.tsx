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
        // Backend is offline, ignore gracefully instead of throwing console.error
        // which triggers Next.js red error overlay
        setActiveJobs([]);
      }
    };
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // poll every 5s
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
      // Backend is offline, show alert instead of throwing console.error
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

  return (
    <>
      {/* Submit Job Modal Overlay */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-surface border border-border-base w-full max-w-md shadow-2xl rounded-sm">
            <div className="border-b border-border-base px-6 py-4 flex justify-between items-center bg-surface">
              <h2 className="font-mono text-sm font-bold text-primary uppercase tracking-wider">Deploy New Job</h2>
              <button onClick={() => setShowSubmitModal(false)} className="text-secondary hover:text-error-crimson">
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
            </div>
            
            <form onSubmit={handleCreateJob} className="p-6 space-y-4">
              <div>
                <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Job Alias</label>
                <input required name="job_name" type="text" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-sm" placeholder="e.g. edge_detect_batch_01" />
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Strategy Type</label>
                  <select name="job_type" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm">
                    <option value="math">Math / Compute</option>
                    <option value="image">Image Processing</option>
                    <option value="crypto">Cryptography</option>
                  </select>
                </div>
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Target Pool</label>
                  <select name="pool_id" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm">
                    <option value="public_pool">public_pool</option>
                    <option value="private_cluster_01">private_cluster_01</option>
                  </select>
                </div>
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Compute Mode</label>
                  <select name="compute_mode" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm">
                    <option value="any">Any (Hybrid)</option>
                    <option value="gpu_only">GPU Only</option>
                    <option value="cpu_only">CPU Only</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Data Payload (File)</label>
                <input required name="file" type="file" className="w-full bg-surface border border-border-base px-3 py-1.5 text-sm font-mono file:mr-4 file:py-1 file:px-3 file:border-0 file:text-xs file:font-mono file:bg-surface-container file:text-primary hover:file:bg-primary hover:file:text-on-primary focus:outline-none cursor-pointer rounded-sm" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Max Worker Nodes</label>
                  <input required name="max_workers" type="number" min="1" max="1000" defaultValue={10} className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm" />
                  <p className="text-[10px] text-secondary mt-1 font-mono">Limit how many chunks this payload can be split into.</p>
                </div>
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Access Password (Optional)</label>
                  <input name="password" type="text" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm" placeholder="Leave blank for public access" />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setShowSubmitModal(false)} className="px-4 py-2 text-sm font-mono uppercase text-secondary hover:bg-surface-container transition-colors rounded-sm border border-transparent">Abort</button>
                <button disabled={isSubmitting} type="submit" className="px-6 py-2 text-sm font-mono uppercase bg-primary text-on-primary hover:opacity-90 transition-opacity rounded-sm border border-primary flex items-center gap-2">
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
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold font-sans text-primary mb-1">My Jobs</h1>
          <p className="text-sm font-sans text-secondary">Manage and monitor tasks you have submitted to the grid.</p>
        </div>
        <button 
          onClick={() => setShowSubmitModal(true)} 
          className="px-4 py-2 bg-primary text-on-primary text-sm font-mono uppercase tracking-wider hover:opacity-90 transition-opacity rounded-sm border border-primary flex items-center gap-2 shadow-sm"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
          New Job
        </button>
      </div>

      {/* Main Table */}
      <section className="bg-surface border border-border-base rounded-sm shadow-sm overflow-hidden">
        <div className="px-margin-md py-3 border-b border-border-base bg-surface">
          <h2 className="text-sm font-bold text-primary font-mono uppercase tracking-wider">Active & Recent Jobs</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-bg-subtle text-[10px] font-mono text-secondary uppercase tracking-widest border-b border-border-base">
                <th className="px-margin-md py-3 font-medium">Job ID</th>
                <th className="px-margin-md py-3 font-medium">Alias</th>
                <th className="px-margin-md py-3 font-medium">Type</th>
                <th className="px-margin-md py-3 font-medium">Status</th>
                <th className="px-margin-md py-3 font-medium">Global Progress</th>
                <th className="px-margin-md py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm font-sans">
              {activeJobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-margin-md py-8 text-center text-secondary font-mono text-xs">
                    No active jobs. Deploy a new job to begin compute.
                  </td>
                </tr>
              ) : (
                activeJobs.map((job) => (
                  <tr 
                    key={job.job_id} 
                    onClick={() => router.push(`/orchestrator/job/${job.job_id}`)}
                    className="cursor-pointer hover:bg-bg-subtle transition-colors border-b border-border-base/50 last:border-0 group"
                  >
                    <td className="px-margin-md py-4 font-mono font-medium text-primary">#{job.job_id.substring(0, 12)}</td>
                    <td className="px-margin-md py-4 font-medium">{job.job_name}</td>
                    <td className="px-margin-md py-4 text-secondary">{job.job_type}</td>
                    <td className="px-margin-md py-4">
                      <span className={`inline-flex items-center gap-1.5 ${job.status === 'processing' ? 'text-success-emerald' : 'text-secondary'}`}>
                        <span className={job.status === 'processing' ? 'active-dot' : 'w-1.5 h-1.5 rounded-full bg-border-hover'}></span> 
                        {job.status}
                      </span>
                    </td>
                    <td className="px-margin-md py-4 w-64">
                      <div className="flex items-center gap-3">
                        <div className="flex-grow bg-surface-container rounded-full h-1.5 relative overflow-hidden">
                          <div className={`rounded-full h-1.5 transition-all duration-500 ${job.status === 'Active' ? 'bg-success-emerald' : 'bg-primary/30'}`} style={{ width: `${job.progress}%` }}></div>
                        </div>
                        <span className="font-mono text-[10px] text-secondary w-8">{job.progress}%</span>
                      </div>
                    </td>
                    <td className="px-margin-md py-4 text-right">
                      <div className="flex justify-end gap-2">
                        {(job.status === 'completed' || job.status === 'halted') && (
                          <button 
                            onClick={(e) => handleDeleteJob(job.job_id, e)}
                            className="px-2 py-1 text-[10px] font-mono uppercase border border-error-crimson/50 hover:bg-error-crimson hover:text-white text-error-crimson transition-colors rounded-sm flex items-center justify-center"
                            title="Delete Job"
                          >
                            <span className="material-symbols-outlined text-[14px]">delete</span>
                          </button>
                        )}
                        <Link href={`/orchestrator/job/${job.job_id}`} className="px-3 py-1 flex items-center justify-center text-[10px] font-mono uppercase border border-border-base hover:border-primary text-secondary hover:text-primary transition-colors rounded-sm">
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
