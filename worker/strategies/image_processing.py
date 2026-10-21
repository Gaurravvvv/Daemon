import logging
import os
import zipfile
import tempfile
import numpy as np
from PIL import Image
import time
from storage import storage

logger = logging.getLogger(__name__)

# ── Auto-detect GPU availability with active smoke test ──
USE_GPU = False
if os.environ.get("FORCE_CPU", "").lower() not in ("1", "true", "yes"):
    try:
        import cupy as cp  # type: ignore
        if cp.cuda.runtime.getDeviceCount() > 0:
            device_id = int(os.environ.get("GPU_DEVICE_ID", "0"))
            if device_id >= cp.cuda.runtime.getDeviceCount():
                device_id = 0
            cp.cuda.Device(device_id).use()

            # Active compute verification: tests memory allocation & kernel compilation
            _test = cp.zeros(2, dtype=cp.float32)
            _test += 1.0
            cp.cuda.Stream.null.synchronize()
            del _test
            cp.get_default_memory_pool().free_all_blocks()

            USE_GPU = True
            dev_props = cp.cuda.runtime.getDeviceProperties(device_id)
            dev_name = dev_props.get("name", b"Unknown GPU")
            if isinstance(dev_name, bytes):
                dev_name = dev_name.decode("utf-8", errors="replace")
            logger.info(f"[ImageStrategy] GPU ENABLED: {dev_name} (Device {device_id})")
        else:
            logger.info("[ImageStrategy] CuPy found but no CUDA device detected. Using CPU fallback.")
    except ImportError:
        logger.info("[ImageStrategy] CuPy not available. Using CPU (NumPy) fallback.")
    except Exception as e:
        logger.warning(f"[ImageStrategy] GPU initialization/compute test failed ({e}). Using CPU fallback.")
else:
    logger.info("[ImageStrategy] FORCE_CPU set. Running on CPU.")


def _sobel_edge_detect(img_array, use_gpu: bool = True):
    """Apply Sobel edge detection using GPU tensors (CuPy) or CPU (NumPy)."""
    if use_gpu:
        import cupy as xp  # type: ignore
    else:
        import numpy as xp

    # Convert to float32 for math
    img_f = xp.asarray(img_array, dtype=xp.float32)
    
    # If color image, convert to grayscale luminance first (0.2989 R + 0.5870 G + 0.1140 B)
    if img_f.ndim == 3:
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
    padded = xp.pad(gray, 1, mode='edge')
    
    # 2D convolution - skip zero-weight cells to save GPU memory and ops
    gx = xp.zeros_like(gray)
    gy = xp.zeros_like(gray)
    for i in range(3):
        for j in range(3):
            kx = sobel_x[i, j]
            if kx != 0:
                gx += kx * padded[i:i+h, j:j+w]
            ky = sobel_y[i, j]
            if ky != 0:
                gy += ky * padded[i:i+h, j:j+w]
    
    # Gradient magnitude
    edges = xp.sqrt(gx**2 + gy**2)
    
    # Normalize to 0-255
    edges = (edges / (edges.max() + 1e-5)) * 255.0
    return edges.astype(xp.uint8)


def _contrast_enhance(img_array, factor=1.5, use_gpu: bool = True):
    """Contrast enhancement via histogram stretching."""
    if use_gpu:
        import cupy as xp  # type: ignore
    else:
        import numpy as xp

    img_f = xp.asarray(img_array, dtype=xp.float32)
    mean_val = xp.mean(img_f)
    enhanced = (img_f - mean_val) * factor + mean_val
    enhanced = xp.clip(enhanced, 0, 255)
    return enhanced.astype(xp.uint8)


class ImageProcessingStrategy:
    @staticmethod
    def execute(task_payload: dict) -> dict:
        global USE_GPU
        task_id = task_payload.get("task_id")
        job_id = task_payload.get("job_id")
        raw_data_url = task_payload.get("raw_data_url")
        chunk_index = task_payload.get("chunk_index", 0)
        compute_mode = task_payload.get("compute_mode", "any")

        # Honor explicit cpu_only requests
        if compute_mode == "cpu_only":
            run_on_gpu = False
            device_name = "CPU (forced by task)"
        else:
            run_on_gpu = USE_GPU
            device_name = "GPU" if run_on_gpu else "CPU"
        
        logger.info(f"[ImageStrategy] Executing task {task_id} on {device_name} (compute_mode: {compute_mode})")
        
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
        actual_device = device_name
        if run_on_gpu:
            try:
                import cupy as cp  # type: ignore
                # Stage 1: Sobel Edge Detection (CUDA convolution)
                edges_gpu = _sobel_edge_detect(img_array, use_gpu=True)
                
                # Stage 2: Contrast Enhancement on original
                enhanced_gpu = _contrast_enhance(img_array, use_gpu=True)
                
                # Transfer back to host CPU memory
                edges_cpu = cp.asnumpy(edges_gpu)
                enhanced_cpu = cp.asnumpy(enhanced_gpu)
                
                # Explicit cleanup of device tensors and memory pool
                del edges_gpu, enhanced_gpu
                cp.get_default_memory_pool().free_all_blocks()
                
            except Exception as gpu_err:
                logger.warning(f"[ImageStrategy] GPU processing failed ({gpu_err}), falling back to CPU")
                try:
                    import cupy as cp  # type: ignore
                    cp.get_default_memory_pool().free_all_blocks()
                    cp.get_default_pinned_memory_pool().free_all_blocks()
                except Exception:
                    pass
                
                USE_GPU = False
                edges_cpu = _sobel_edge_detect(img_array, use_gpu=False)
                enhanced_cpu = _contrast_enhance(img_array, use_gpu=False)
                actual_device = "CPU (fallback)"
        else:
            edges_cpu = _sobel_edge_detect(img_array, use_gpu=False)
            enhanced_cpu = _contrast_enhance(img_array, use_gpu=False)
        
        elapsed = round(time.time() - start_time, 4)
        logger.info(f"[ImageStrategy] Processing completed on [{actual_device}] in {elapsed}s")
        
        # 6. Save both results
        base_name = os.path.basename(target_image_name)
        name_stem = os.path.splitext(base_name)[0]
        ext = os.path.splitext(base_name)[1] or ".jpg"
        
        edges_path = os.path.join(extract_dir, f"edges_{name_stem}{ext}")
        Image.fromarray(edges_cpu).save(edges_path)
        
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
