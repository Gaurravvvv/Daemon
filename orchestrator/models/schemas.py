from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class JobSubmitRequest(BaseModel):
    job_name: str = Field(..., description="Name of the job")
    job_type: str = Field(..., description="Type of job (e.g., image_processing, math)")
    pool_id: str = Field(..., description="Target pool (e.g., public_pool, user_1_pool)")
    raw_data_url: str = Field(..., description="MinIO URL to raw dataset")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Job specific params")

class JobSubmitResponse(BaseModel):
    job_id: str
    status: str

class WorkerRegisterRequest(BaseModel):
    worker_id: str
    pool_id: str
    capabilities: list[str]
    system_info: Dict[str, Any]

class WorkerRegisterResponse(BaseModel):
    status: str
    heartbeat_interval: int
