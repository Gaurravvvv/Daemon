from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class JobSubmitRequest(BaseModel):
    job_name: str = Field(..., description="Name of the job")
    job_type: str = Field(..., description="Type of job (e.g., image, math, crypto)")
    pool_id: str = Field(..., description="Target pool (e.g., public_pool, user_1_pool)")
    raw_data_url: str = Field(..., description="MinIO URL to raw dataset")
    compute_mode: str = Field(default="any", description="Compute preference: gpu_only, cpu_only, any")
    split_count: Optional[int] = Field(default=10, description="Number of task partitions")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Job specific params")

class JobSubmitResponse(BaseModel):
    job_id: str
    status: str

class WorkerRegisterRequest(BaseModel):
    worker_id: str
    pool_id: str
    capabilities: List[str]
    system_info: Dict[str, Any]

class WorkerRegisterResponse(BaseModel):
    status: str
    heartbeat_interval: int

class WorkerHeartbeatResponse(BaseModel):
    status: str
    acknowledged: bool

class TaskCompleteRequest(BaseModel):
    total_chunks: int
    status: Optional[str] = "success"  # "success" or "failed"
    chunk_index: Optional[int] = None
    worker_id: Optional[str] = None
    error_message: Optional[str] = None

class VerifyPasswordRequest(BaseModel):
    password: str

