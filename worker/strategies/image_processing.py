import logging
import os
import zipfile
import tempfile
import numpy as np
from PIL import Image
import time
from storage import storage

logger = logging.getLogger(__name__)

# ── Auto-detect GPU availability ──
USE_GPU = False
try:
    import cupy as cp  # type: ignore
    if cp.cuda.runtime.getDeviceCount() > 0:
        USE_GPU = True
        logger.info(f"[ImageStrategy] GPU ENABLED: {cp.cuda.runtime.getDeviceProperties(0)}")
    else:
        logger.info("[ImageStrategy] CuPy found but no GPU detected. Using CPU fallback.")
except ImportError:
    logger.info("[ImageStrategy] CuPy not available. Using CPU (NumPy) fallback.")
except Exception as e:
    logger.warning(f"[ImageStrategy] GPU detection failed: {e}. Using CPU fallback.")

# Choose the array library: CuPy (GPU) or NumPy (CPU)
xp = cp if USE_GPU else np


def _sobel_edge_detect(img_array):
    """Apply Sobel edge detection using GPU tensors (CuPy) or CPU (NumPy)."""
    # Convert to float32 for math
    img_f = xp.asarray(img_array, dtype=xp.float32)
    
    # If color image, convert to grayscale luminance first
    if img_f.ndim == 3:
        # Standard luminance weights: 0.2989 R + 0.5870 G + 0.1140 B
        gray = 0.2989 * img_f[:, :, 0] + 0.5870 * img_f[:, :, 1] + 0.1140 * img_f[:, :, 2]
    else:
        gray = img_f

    # Sobel kernels for horizontal and vertical edge detection
    sobel_x = xp.array([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]], dtype=xp.float32)
    sobel_y = xp.array([[-1, -2, -1],
                         [ 0,  0,  0],
                         [ 1,  2,  1]], dtype=xp.float32)

    h, w = gray.shape
    # Pad image for convolution
    padded = xp.pad(gray, 1, mode='edge')
    
    # Manual 2D convolution (runs on GPU CUDA cores if CuPy, CPU if NumPy)
    gx = xp.zeros_like(gray)
    gy = xp.zeros_like(gray)
    for i in range(3):
        for j in range(3):
            gx += sobel_x[i, j] * padded[i:i+h, j:j+w]
            gy += sobel_y[i, j] * padded[i:i+h, j:j+w]
    
    # Gradient magnitude
    edges = xp.sqrt(gx**2 + gy**2)
    
    # Normalize to 0-255
    edges = (edges / (edges.max() + 1e-5)) * 255.0
    return edges.astype(xp.uint8)


def _contrast_enhance(img_array, factor=1.5):
    """GPU-accelerated contrast enhancement via histogram stretching."""
    img_f = xp.asarray(img_array, dtype=xp.float32)
    
    # Center around mean, scale by factor, re-center
    mean_val = xp.mean(img_f)
    enhanced = (img_f - mean_val) * factor + mean_val
    
    # Clamp to valid range
    enhanced = xp.clip(enhanced, 0, 255)
    return enhanced.astype(xp.uint8)


class ImageProcessingStrategy:
    @staticmethod
    def execute(task_payload: dict) -> dict:
        task_id = task_payload.get("task_id")
        job_id = task_payload.get("job_id")
        raw_data_url = task_payload.get("raw_data_url")
        chunk_index = task_payload.get("chunk_index", 0)
        
        device_name = "GPU" if USE_GPU else "CPU"
        logger.info(f"[ImageStrategy] Executing task {task_id} on {device_name}")
        
        # 1. Parse MinIO URL (format: minio://bucket_name/object_name)
        if not raw_data_url.startswith("minio://"):
            raise ValueError(f"Invalid raw_data_url format: {raw_data_url}")
            
        parts = raw_data_url.replace("minio://", "").split("/", 1)
        bucket = parts[0]
        object_name = parts[1]
        
        # 2. Download the ZIP file using cross-platform temp directory
        temp_dir = os.path.join(tempfile.gettempdir(), "daemon_worker")
        os.makedirs(temp_dir, exist_ok=True)
        local_zip_path = os.path.join(temp_dir, f"{job_id}_payload.zip")
        downloaded = storage.download_data(bucket, object_name, local_zip_path)
        if not downloaded:
            raise Exception("Failed to download payload from MinIO")
            
        # 3. Extract the target image based on chunk_index
        extract_dir = os.path.join(temp_dir, f"{task_id}_extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        with zipfile.ZipFile(local_zip_path, 'r') as zf:
            all_files = [
                f for f in zf.namelist() 
                if not f.endswith('/') 
                and f.lower().endswith(valid_extensions)
                and not os.path.basename(f).startswith('.')
            ]
            
            if not all_files:
                raise Exception("No valid image files (.jpg, .png, etc.) found in the uploaded ZIP payload.")
                
            target_image_name = all_files[chunk_index % len(all_files)]
            zf.extract(target_image_name, extract_dir)
            
        img_path = os.path.join(extract_dir, target_image_name)
        
        # 4. Load image into array
        logger.info(f"Processing image {target_image_name} on [{device_name}]...")
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        
        start_time = time.time()
        
        # 5. GPU/CPU Processing Pipeline
        try:
            # Stage 1: Sobel Edge Detection (CUDA convolution)
            edges = _sobel_edge_detect(img_array)
            
            # Stage 2: Contrast Enhancement on original
            enhanced = _contrast_enhance(img_array)
            
            # Transfer back to CPU if on GPU
            if USE_GPU:
                edges_cpu = cp.asnumpy(edges)
                enhanced_cpu = cp.asnumpy(enhanced)
            else:
                edges_cpu = edges
                enhanced_cpu = enhanced
                
            actual_device = device_name
            
        except Exception as gpu_err:
            # OOM or CUDA error → fall back to CPU
            logger.warning(f"[ImageStrategy] GPU processing failed ({gpu_err}), falling back to CPU")
            global xp
            xp = np
            
            edges_cpu = _sobel_edge_detect(img_array)
            enhanced_cpu = _contrast_enhance(img_array)
            actual_device = "CPU (fallback)"
        
        elapsed = round(time.time() - start_time, 4)
        logger.info(f"[ImageStrategy] Processing completed on [{actual_device}] in {elapsed}s")
        
        # 6. Save both results
        base_name = os.path.basename(target_image_name)
        name_stem = os.path.splitext(base_name)[0]
        ext = os.path.splitext(base_name)[1] or ".jpg"
        
        # Save edge detection result
        edges_path = os.path.join(extract_dir, f"edges_{name_stem}{ext}")
        Image.fromarray(edges_cpu).save(edges_path)
        
        # Save contrast enhanced result
        enhanced_path = os.path.join(extract_dir, f"enhanced_{name_stem}{ext}")
        Image.fromarray(enhanced_cpu).save(enhanced_path)
        
        # 7. Upload results back to MinIO
        edges_url = storage.upload_result(bucket, edges_path, f"{job_id}/results/{task_id}_edges_{base_name}")
        enhanced_url = storage.upload_result(bucket, enhanced_path, f"{job_id}/results/{task_id}_enhanced_{base_name}")
        
        logger.info(f"[ImageStrategy] Task {task_id} complete. Edges: {edges_url}, Enhanced: {enhanced_url}")
        
        return {
            "task_id": task_id,
            "status": "success",
            "device": actual_device,
            "processing_time": elapsed,
            "edges_url": edges_url,
            "enhanced_url": enhanced_url,
        }
