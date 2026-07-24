"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function WorkerDashboard() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const publicJobs: any[] = [];

  const filteredJobs = publicJobs.filter(job => 
    job.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    job.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-2xl font-bold font-sans text-primary mb-1">Global Compute Pool</h1>
          <p className="text-sm font-sans text-secondary">Donate your idle hardware to process public tasks and earn rewards.</p>
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

      {filteredJobs.length === 0 ? (
        <div className="mt-12 text-center text-secondary font-mono text-xs">
          No public compute jobs available at the moment.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {filteredJobs.map(job => (
            <div 
              key={job.id} 
              onClick={() => router.push(`/worker/job/${job.id}`)}
              className="cursor-pointer bg-surface border border-border-base rounded-sm p-5 hover:border-primary transition-colors group flex flex-col"
            >
              <div className="flex justify-between items-start mb-4">
                <span className="font-mono text-sm font-bold text-primary px-2 py-1 bg-surface rounded">#{job.id}</span>
                <span className="font-mono text-[10px] text-success-emerald uppercase tracking-wider bg-success-emerald/10 px-2 py-1 rounded">Open</span>
              </div>
              <h3 className="font-sans font-bold text-base mb-1 text-primary">{job.name}</h3>
              <span className="font-mono text-xs text-secondary mb-6">{job.type}</span>
              
              <div className="mt-auto pt-4 border-t border-border-base flex justify-between items-center text-sm font-sans">
                <div className="flex items-center gap-1.5 text-secondary">
                  <span className="material-symbols-outlined text-[16px]">database</span>
                  {job.payloadSize}
                </div>
                <div className="flex items-center gap-1.5 text-secondary">
                  <span className="material-symbols-outlined text-[16px]">grid_on</span>
                  {job.chunks}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
