"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function OrchestratorDashboard() {
  const router = useRouter();
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Mock data for the table, in a real app this would fetch from /api/jobs
  const activeJobs: any[] = [];

  const handleCreateJob = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate API call to create job, then route to the job details page
    setTimeout(() => {
      setShowSubmitModal(false);
      setIsSubmitting(false);
      router.push("/orchestrator/job/9999");
    }, 800);
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
                <input required type="text" className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-sm" placeholder="e.g. hash_verifier_batch_A" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Strategy Type</label>
                  <select className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm">
                    <option>Math / Compute</option>
                    <option>Image Processing</option>
                    <option>Cryptography</option>
                  </select>
                </div>
                <div>
                  <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Target Pool</label>
                  <select className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm">
                    <option>public_pool</option>
                    <option>private_cluster_01</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-mono text-xs font-semibold text-secondary uppercase block mb-1.5">Max Worker Nodes</label>
                <input required type="number" defaultValue={100} className="w-full bg-surface border border-border-base px-3 py-2 text-sm font-sans focus:outline-none focus:border-primary rounded-sm" />
                <p className="text-[10px] text-secondary mt-1 font-mono">Limit how many chunks this payload can be split into.</p>
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
                    key={job.id} 
                    onClick={() => router.push(`/orchestrator/job/${job.id}`)}
                    className="cursor-pointer hover:bg-bg-subtle transition-colors border-b border-border-base/50 last:border-0 group"
                  >
                    <td className="px-margin-md py-4 font-mono font-medium text-primary">#{job.id}</td>
                    <td className="px-margin-md py-4 font-medium">{job.name}</td>
                    <td className="px-margin-md py-4 text-secondary">{job.type}</td>
                    <td className="px-margin-md py-4">
                      <span className={`inline-flex items-center gap-1.5 ${job.status === 'Active' ? 'text-success-emerald' : 'text-secondary'}`}>
                        <span className={job.status === 'Active' ? 'active-dot' : 'w-1.5 h-1.5 rounded-full bg-border-hover'}></span> 
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
                      <Link href={`/orchestrator/job/${job.id}`} className="px-3 py-1 text-[10px] font-mono uppercase border border-border-base hover:border-primary text-secondary hover:text-primary transition-colors rounded-sm">
                        Inspect
                      </Link>
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
