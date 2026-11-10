"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function OrchestratorDashboard() {
  const router = useRouter();
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [selectedJobType, setSelectedJobType] = useState("csv_cleaning");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeJobs, setActiveJobs] = useState<any[]>([]);
  const [activeWorkerCount, setActiveWorkerCount] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "processing" | "completed" | "halted">("all");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [jobsRes, workersRes] = await Promise.allSettled([
          fetch("http://127.0.0.1:8000/api/v1/jobs"),
          fetch("http://127.0.0.1:8000/api/v1/workers")
        ]);
        if (jobsRes.status === "fulfilled" && jobsRes.value.ok) {
          const data = await jobsRes.value.json();
          setActiveJobs(data.jobs || []);
        }
        if (workersRes.status === "fulfilled" && workersRes.value.ok) {
          const wdata = await workersRes.value.json();
          setActiveWorkerCount(wdata.active_count ?? (wdata.workers?.length || 0));
        }
      } catch (e) {
        setActiveJobs([]);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateJob = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const formData = new FormData(e.currentTarget);
    const rules = {
      deduplicate: formData.get("rule_dedup") === "on",
      standardize_nulls: formData.get("rule_nulls") === "on",
      redact_pii: formData.get("rule_pii") === "on",
      standardize_dates: formData.get("rule_dates") === "on",
      clean_headers: true
    };
    formData.append("rules_json", JSON.stringify(rules));
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/jobs/upload_and_submit", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      setShowSubmitModal(false);
      setSelectedFile(null);
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
  const haltedCount = activeJobs.filter(j => j.status === 'halted').length;
  const totalChunks = activeJobs.reduce((acc, curr) => acc + (curr.total_chunks || 10), 0);

  const filteredJobs = activeJobs.filter(job => {
    if (statusFilter !== "all" && job.status !== statusFilter) return false;
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      (job.job_name || "").toLowerCase().includes(q) ||
      (job.job_id || "").toLowerCase().includes(q) ||
      (job.job_type || "").toLowerCase().includes(q)
    );
  });

  const formatStrategyName = (type: string) => {
    switch ((type || "").toLowerCase()) {
      case "csv_cleaning":
      case "csv":
      case "tabular":
      case "data_cleaning":
        return "CSV Cleaning";
      case "math":
      case "matrix":
      case "matrix_multiplication":
        return "Matrix Compute";
      case "image":
      case "image_processing":
        return "Image Processing";
      case "crypto":
      case "cryptography":
        return "Cryptography";
      default:
        return type || "Compute";
    }
  };

  return (
    <>
      {/* Submit Job Modal Overlay */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-3 sm:p-4">
          <div className="bg-surface border border-border-base w-full max-w-xl sm:max-w-2xl max-h-[90vh] flex flex-col rounded-[16px] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="border-b border-border-base px-6 py-4 flex justify-between items-center bg-surface-container shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-[8px] bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[18px]">terminal</span>
                </div>
                <div>
                  <h2 className="micro-label font-bold text-foreground">Deploy Compute Workload</h2>
                  <p className="font-sans text-[11px] text-secondary mt-0.5">Configure task partitioning and dispatch to the worker mesh</p>
                </div>
              </div>
              <button 
                type="button"
                onClick={() => {
                  setShowSubmitModal(false);
                  setSelectedFile(null);
                }} 
                className="text-secondary hover:text-foreground p-1.5 rounded-[6px] hover:bg-surface transition-colors inline-flex items-center justify-center"
                title="Close Modal"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>
            
            <form onSubmit={handleCreateJob} className="p-5 sm:p-6 space-y-4 sm:space-y-5 overflow-y-auto custom-scrollbar flex-1">
              {/* Job Alias */}
              <div>
                <label className="micro-label text-secondary block mb-1.5">Job Alias / Identifier</label>
                <input 
                  required 
                  name="job_name" 
                  type="text" 
                  className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-sans text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px] transition-all placeholder:text-secondary/50" 
                  placeholder="e.g. distributed_data_cleaning_batch_01" 
                />
              </div>
              
              {/* Strategy & Compute Configuration */}
              <div className="space-y-3">
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Workload Strategy</label>
                  <select 
                    name="job_type" 
                    value={selectedJobType}
                    onChange={(e) => setSelectedJobType(e.target.value)}
                    className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-sans text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px] cursor-pointer"
                  >
                    <option value="csv_cleaning">Structured CSV Dataset Cleaning (Schema-Agnostic)</option>
                    <option value="math">Distributed Matrix Multiplication</option>
                    <option value="image">Image Processing and Edge Detection</option>
                    <option value="crypto">Cryptographic Search and Proof-of-Work</option>
                  </select>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="micro-label text-secondary block mb-1.5">Target Worker Pool</label>
                    <select name="pool_id" className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-sans text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px] cursor-pointer">
                      <option value="public_pool">Public_pool (Open Compute Grid)</option>
                      <option value="private_cluster_01">Private_cluster_01 (Dedicated Nodes)</option>
                    </select>
                  </div>
                  <div>
                    <label className="micro-label text-secondary block mb-1.5">Compute Acceleration Mode</label>
                    <select name="compute_mode" className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-sans text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px] cursor-pointer">
                      <option value="any">Any (Hybrid CPU/GPU)</option>
                      <option value="gpu_only">GPU Accelerated (CUDA)</option>
                      <option value="cpu_only">CPU Only (NumPy)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Distributed Cleaning Rules (Schema-Agnostic) */}
              {selectedJobType === "csv_cleaning" && (
                <div className="p-4 bg-surface-container/60 rounded-[12px] border border-border-base space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="micro-label text-primary font-bold">Distributed Cleaning Rules (Schema-Agnostic)</span>
                    <span className="text-[10px] font-mono text-secondary px-2 py-0.5 rounded bg-surface border border-border-base">ETL Engine</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    <label className="flex items-start gap-2.5 p-2.5 rounded-[8px] bg-surface border border-border-base/70 hover:border-primary/50 transition-colors cursor-pointer group">
                      <input type="checkbox" name="rule_dedup" defaultChecked className="mt-0.5 accent-primary h-4 w-4 rounded cursor-pointer shrink-0" />
                      <div className="min-w-0">
                        <span className="font-sans font-medium text-xs text-foreground group-hover:text-primary transition-colors block">Drop Duplicate Rows</span>
                        <span className="font-sans text-[11px] text-secondary leading-tight block mt-0.5">Streaming hash matching eliminates duplicate records</span>
                      </div>
                    </label>

                    <label className="flex items-start gap-2.5 p-2.5 rounded-[8px] bg-surface border border-border-base/70 hover:border-primary/50 transition-colors cursor-pointer group">
                      <input type="checkbox" name="rule_nulls" defaultChecked className="mt-0.5 accent-primary h-4 w-4 rounded cursor-pointer shrink-0" />
                      <div className="min-w-0">
                        <span className="font-sans font-medium text-xs text-foreground group-hover:text-primary transition-colors block">Sanitize Sentinel Nulls</span>
                        <span className="font-sans text-[11px] text-secondary leading-tight block mt-0.5">Standardizes missing, null, and sentinel entries to empty cells</span>
                      </div>
                    </label>

                    <label className="flex items-start gap-2.5 p-2.5 rounded-[8px] bg-surface border border-border-base/70 hover:border-primary/50 transition-colors cursor-pointer group">
                      <input type="checkbox" name="rule_pii" defaultChecked className="mt-0.5 accent-primary h-4 w-4 rounded cursor-pointer shrink-0" />
                      <div className="min-w-0">
                        <span className="font-sans font-medium text-xs text-foreground group-hover:text-primary transition-colors block">Scrub PII Entities</span>
                        <span className="font-sans text-[11px] text-secondary leading-tight block mt-0.5">Redacts emails, phone numbers and card identifiers</span>
                      </div>
                    </label>

                    <label className="flex items-start gap-2.5 p-2.5 rounded-[8px] bg-surface border border-border-base/70 hover:border-primary/50 transition-colors cursor-pointer group">
                      <input type="checkbox" name="rule_dates" defaultChecked className="mt-0.5 accent-primary h-4 w-4 rounded cursor-pointer shrink-0" />
                      <div className="min-w-0">
                        <span className="font-sans font-medium text-xs text-foreground group-hover:text-primary transition-colors block">Normalize Date Formats</span>
                        <span className="font-sans text-[11px] text-secondary leading-tight block mt-0.5">Standardizes mixed date notations to ISO-8601</span>
                      </div>
                    </label>
                  </div>
                </div>
              )}

              {/* Styled File Upload Dropzone */}
              <div>
                <label className="micro-label text-secondary block mb-1.5">Payload Dataset (.CSV or .ZIP)</label>
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="border border-dashed border-border-base hover:border-primary/60 bg-surface-container/40 hover:bg-surface-container/70 transition-all rounded-[12px] p-4 text-center cursor-pointer group"
                >
                  <input 
                    ref={fileInputRef}
                    required 
                    name="file" 
                    type="file" 
                    accept=".csv,.zip,.txt"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="hidden" 
                  />
                  {selectedFile ? (
                    <div className="flex items-center justify-between gap-3 px-2">
                      <div className="flex items-center gap-2.5 text-left min-w-0">
                        <div className="w-8 h-8 rounded-[8px] bg-primary/10 border border-primary/30 flex items-center justify-center shrink-0 text-primary">
                          <span className="material-symbols-outlined text-[18px]">description</span>
                        </div>
                        <div className="min-w-0">
                          <span className="font-mono text-xs text-foreground font-medium truncate block">
                            {selectedFile.name}
                          </span>
                          <span className="text-[11px] font-mono text-secondary block">
                            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                          </span>
                        </div>
                      </div>
                      <span className="ide-chip border-primary/40 text-primary text-[10px] shrink-0">
                        Ready to Upload
                      </span>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center gap-1.5 py-1">
                      <span className="material-symbols-outlined text-[24px] text-secondary group-hover:text-primary transition-colors">
                        upload_file
                      </span>
                      <span className="font-sans text-xs text-foreground group-hover:text-primary transition-colors font-medium">
                        Click to browse or drag and drop dataset file
                      </span>
                      <span className="font-mono text-[10px] text-secondary">
                        Supported: .csv, .zip, .txt (up to 2 GB)
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Split Count & Password */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="micro-label text-secondary">Split Count (Partitions)</label>
                    <span className="text-[10px] font-mono text-secondary">1 - 100</span>
                  </div>
                  <input 
                    name="split_count" 
                    type="number" 
                    defaultValue="10" 
                    min="1" 
                    max="100" 
                    className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-mono text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px]" 
                  />
                </div>
                <div>
                  <label className="micro-label text-secondary block mb-1.5">Access Password (Optional)</label>
                  <input 
                    name="password" 
                    type="password" 
                    placeholder="None (Public Pool)" 
                    className="w-full h-10 bg-surface border border-border-base px-3 text-xs sm:text-sm font-sans text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-[8px] placeholder:text-secondary/50" 
                  />
                </div>
              </div>

              {/* Footer */}
              <div className="pt-3 border-t border-border-base flex items-center justify-between gap-3 shrink-0">
                <div className="text-[11px] font-mono text-secondary hidden sm:flex items-center gap-1.5">
                  <span className="active-dot"></span>
                  Grid Ready
                </div>
                <div className="flex items-center gap-3 ml-auto">
                  <button 
                    type="button" 
                    onClick={() => {
                      setShowSubmitModal(false);
                      setSelectedFile(null);
                    }} 
                    className="px-4 py-2 text-xs micro-label text-secondary hover:text-foreground hover:bg-surface-container transition-all rounded-[8px] border border-transparent"
                  >
                    Cancel
                  </button>
                  <button 
                    disabled={isSubmitting} 
                    type="submit" 
                    className="btn-interactive px-5 py-2 text-xs micro-label bg-primary text-on-primary font-bold rounded-[8px] border border-primary flex items-center gap-2 shadow-sm disabled:opacity-50"
                  >
                    {isSubmitting ? (
                      <>
                        <span>Deploying</span>
                        <span className="material-symbols-outlined text-[14px] animate-spin">sync</span>
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined text-[15px]">send</span>
                        <span>Deploy to Grid</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold title-tight text-primary mb-1">Orchestrator Console</h1>
          <p className="text-xs sm:text-sm font-sans text-secondary">Manage, schedule, and track distributed jobs dispatched to the edge compute grid.</p>
        </div>
        <button 
          onClick={() => setShowSubmitModal(true)} 
          className="btn-interactive w-full sm:w-auto px-4 py-2.5 bg-primary text-on-primary text-xs micro-label font-bold rounded-[8px] border border-primary flex items-center justify-center gap-2 shadow-sm shrink-0"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
          Deploy New Job
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between min-h-[100px]">
          <div className="flex items-center justify-between">
            <span className="micro-label text-secondary">Active Processing</span>
            <span className="material-symbols-outlined text-[18px] text-primary">hourglass_top</span>
          </div>
          <div className="mt-2 flex items-baseline justify-between gap-2">
            <span className="kpi-numeral text-2xl sm:text-3xl text-primary">{processingCount}</span>
            <span className="ide-chip border-success-emerald/30 text-success-emerald text-[10px] shrink-0">RUNNING</span>
          </div>
        </div>

        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between min-h-[100px]">
          <div className="flex items-center justify-between">
            <span className="micro-label text-secondary">Completed Jobs</span>
            <span className="material-symbols-outlined text-[18px] text-foreground/70">task_alt</span>
          </div>
          <div className="mt-2 flex items-baseline justify-between gap-2">
            <span className="kpi-numeral text-2xl sm:text-3xl text-foreground">{completedCount}</span>
            <span className="ide-chip border-border-base text-secondary text-[10px] shrink-0">HISTORICAL</span>
          </div>
        </div>

        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between min-h-[100px]">
          <div className="flex items-center justify-between">
            <span className="micro-label text-secondary">Total Task Chunks</span>
            <span className="material-symbols-outlined text-[18px] text-secondary">splitscreen</span>
          </div>
          <div className="mt-2 flex items-baseline justify-between gap-2">
            <span className="kpi-numeral text-2xl sm:text-3xl text-secondary">{totalChunks}</span>
            <span className="ide-chip border-border-base text-secondary text-[10px] shrink-0">PARTITIONS</span>
          </div>
        </div>

        <div className="card-interactive bg-surface border border-border-base rounded-[12px] p-4 flex flex-col justify-between min-h-[100px]">
          <div className="flex items-center justify-between">
            <span className="micro-label text-secondary">Active Nodes / Queue</span>
            <span className="material-symbols-outlined text-[18px] text-success-emerald">hub</span>
          </div>
          <div className="mt-2 flex items-baseline justify-between gap-2">
            <span className="kpi-numeral text-xl sm:text-2xl text-success-emerald truncate">
              {activeWorkerCount} {activeWorkerCount === 1 ? 'Node' : 'Nodes'}
            </span>
            <div className="flex items-center gap-1.5 ide-chip border-success-emerald/30 text-success-emerald text-[10px] shrink-0">
              <span className="active-dot"></span>
              AMQP LIVE
            </div>
          </div>
        </div>
      </div>

      {/* Main Jobs Table with Filter Toolbar */}
      <section className="bg-surface border border-border-base rounded-[16px] overflow-hidden shadow-sm">
        {/* Table Toolbar */}
        <div className="px-4 sm:px-margin-md py-3 border-b border-border-base bg-surface-container flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          {/* Status Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => setStatusFilter("all")}
              className={`px-2.5 py-1 text-[11px] font-mono rounded-[6px] transition-all border ${
                statusFilter === "all"
                  ? "bg-primary text-on-primary font-bold border-primary shadow-xs"
                  : "bg-surface text-secondary hover:text-foreground border-border-base"
              }`}
            >
              All ({activeJobs.length})
            </button>
            <button
              onClick={() => setStatusFilter("processing")}
              className={`px-2.5 py-1 text-[11px] font-mono rounded-[6px] transition-all border ${
                statusFilter === "processing"
                  ? "bg-primary text-on-primary font-bold border-primary shadow-xs"
                  : "bg-surface text-secondary hover:text-foreground border-border-base"
              }`}
            >
              Processing ({processingCount})
            </button>
            <button
              onClick={() => setStatusFilter("completed")}
              className={`px-2.5 py-1 text-[11px] font-mono rounded-[6px] transition-all border ${
                statusFilter === "completed"
                  ? "bg-primary text-on-primary font-bold border-primary shadow-xs"
                  : "bg-surface text-secondary hover:text-foreground border-border-base"
              }`}
            >
              Completed ({completedCount})
            </button>
            {haltedCount > 0 && (
              <button
                onClick={() => setStatusFilter("halted")}
                className={`px-2.5 py-1 text-[11px] font-mono rounded-[6px] transition-all border ${
                  statusFilter === "halted"
                    ? "bg-primary text-on-primary font-bold border-primary shadow-xs"
                    : "bg-surface text-secondary hover:text-foreground border-border-base"
                }`}
              >
                Halted ({haltedCount})
              </button>
            )}
          </div>

          {/* Search Box */}
          <div className="relative w-full md:w-64 shrink-0">
            <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-secondary text-[16px] pointer-events-none">
              search
            </span>
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search alias, ID, strategy..."
              className="w-full h-8 bg-surface border border-border-base rounded-[6px] pl-8 pr-7 text-xs font-mono text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-secondary/50"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-secondary hover:text-foreground"
              >
                <span className="material-symbols-outlined text-[14px]">close</span>
              </button>
            )}
          </div>
        </div>
        
        {/* Table Body */}
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-bg-subtle text-[11px] font-mono text-secondary uppercase tracking-[0.4px] border-b border-border-base">
                <th className="px-4 sm:px-margin-md py-3 font-semibold whitespace-nowrap">Job ID</th>
                <th className="px-4 sm:px-margin-md py-3 font-semibold min-w-[150px]">Alias</th>
                <th className="px-4 sm:px-margin-md py-3 font-semibold whitespace-nowrap">Strategy</th>
                <th className="px-4 sm:px-margin-md py-3 font-semibold whitespace-nowrap">Status</th>
                <th className="px-4 sm:px-margin-md py-3 font-semibold min-w-[180px]">Cluster Progress</th>
                <th className="px-4 sm:px-margin-md py-3 font-semibold text-right whitespace-nowrap">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm font-sans">
              {filteredJobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 sm:px-margin-md py-12 text-center text-secondary font-mono text-xs">
                    <span className="material-symbols-outlined text-3xl mb-2 text-secondary/40 block">inbox</span>
                    {activeJobs.length === 0 ? (
                      <div className="space-y-3">
                        <p>No active jobs in the queue. Deploy a new job above to begin compute.</p>
                        <button
                          onClick={() => setShowSubmitModal(true)}
                          className="btn-interactive px-3.5 py-1.5 text-xs micro-label bg-primary text-on-primary font-bold rounded-[6px] border border-primary inline-flex items-center gap-1.5 shadow-sm"
                        >
                          <span className="material-symbols-outlined text-[14px]">add</span>
                          Deploy First Job
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <p>No jobs found matching the current search and status filters.</p>
                        <button
                          onClick={() => {
                            setSearchQuery("");
                            setStatusFilter("all");
                          }}
                          className="text-primary hover:underline font-sans text-xs"
                        >
                          Reset Filters
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ) : (
                filteredJobs.map((job) => (
                  <tr 
                    key={job.job_id} 
                    onClick={() => router.push(`/orchestrator/job/${job.job_id}`)}
                    className="cursor-pointer hover:bg-surface-container/60 transition-colors border-b border-border-base/60 last:border-0 group"
                  >
                    <td className="px-4 sm:px-margin-md py-3.5 whitespace-nowrap">
                      <span className="ide-chip font-bold text-primary border-primary/30 group-hover:border-primary">
                        #{job.job_id.substring(0, 10)}
                      </span>
                    </td>
                    <td className="px-4 sm:px-margin-md py-3.5 font-semibold text-foreground max-w-[220px] truncate" title={job.job_name}>{job.job_name}</td>
                    <td className="px-4 sm:px-margin-md py-3.5 whitespace-nowrap">
                      <span className="ide-chip text-[10px] font-sans font-medium">
                        {formatStrategyName(job.job_type)}
                      </span>
                    </td>
                    <td className="px-4 sm:px-margin-md py-3.5 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 font-mono text-xs ${
                        job.status === 'processing' ? 'text-success-emerald font-semibold' :
                        job.status === 'completed' ? 'text-primary' :
                        job.status === 'halted' ? 'text-error-crimson' :
                        'text-secondary'
                      }`}>
                        <span className={job.status === 'processing' ? 'active-dot' : 'w-1.5 h-1.5 rounded-full bg-border-base'}></span> 
                        {job.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 sm:px-margin-md py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="flex-grow bg-surface-container rounded-full h-2 relative overflow-hidden border border-border-base/50 min-w-[80px]">
                          <div 
                            className={`rounded-full h-full transition-all duration-500 ${
                              job.status === 'processing' ? 'bg-success-emerald' : 
                              job.status === 'completed' ? 'bg-primary' :
                              'bg-primary/50'
                            }`} 
                            style={{ width: `${job.progress || 0}%` }}
                          ></div>
                        </div>
                        <span className="font-mono text-[11px] text-secondary font-medium w-9 shrink-0">{job.progress || 0}%</span>
                      </div>
                    </td>
                    <td className="px-4 sm:px-margin-md py-3.5 text-right whitespace-nowrap">
                      <div className="flex justify-end items-center gap-2">
                        <button 
                          onClick={(e) => handleDeleteJob(job.job_id, e)}
                          className="px-2 py-1 text-[11px] font-mono border border-error-crimson/30 hover:bg-error-crimson/15 text-error-crimson transition-all rounded-[6px] inline-flex items-center justify-center"
                          title="Delete Job"
                        >
                          <span className="material-symbols-outlined text-[15px]">delete</span>
                        </button>
                        <Link 
                          href={`/orchestrator/job/${job.job_id}`} 
                          className="btn-interactive px-3 py-1 inline-flex items-center justify-center text-[11px] micro-label border border-border-base hover:border-primary text-secondary hover:text-primary transition-all rounded-[6px] bg-surface-container font-semibold"
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
