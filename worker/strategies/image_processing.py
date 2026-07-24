import logging
import os
import zipfile
from PIL import Image, ImageOps
import time
from storage import storage

logger = logging.getLogger(__name__)

class ImageProcessingStrategy:
    @staticmethod
    def execute(task_payload: dict) -> dict:
        task_id = task_payload.get("task_id")
        job_id = task_payload.get("job_id")
        raw_data_url = task_payload.get("raw_data_url")
        chunk_index = task_payload.get("chunk_index", 0)
        
        logger.info(f"[ImageStrategy] Executing task {task_id}")
        
        # 1. Parse MinIO URL (format: minio://bucket_name/object_name)
        if not raw_data_url.startswith("minio://"):
            raise ValueError(f"Invalid raw_data_url format: {raw_data_url}")
            
        parts = raw_data_url.replace("minio://", "").split("/", 1)
        bucket = parts[0]
        object_name = parts[1]
        
        # 2. Download the ZIP file
        local_zip_path = f"/tmp/{job_id}_payload.zip"
        downloaded = storage.download_data(bucket, object_name, local_zip_path)
        if not downloaded:
            raise Exception("Failed to download payload from MinIO")
            
        # 3. Extract the target image based on chunk_index
        extract_dir = f"/tmp/{task_id}_extract"
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(local_zip_path, 'r') as zf:
            # Filter for actual files (not directories)
            all_files = [f for f in zf.namelist() if not f.endswith('/')]
            
            if not all_files:
                raise Exception("No files found in the uploaded ZIP payload.")
                
            # Pick a file based on the chunk index
            target_image_name = all_files[chunk_index % len(all_files)]
            zf.extract(target_image_name, extract_dir)
            
        img_path = os.path.join(extract_dir, target_image_name)
        
        # 4. Process the Image (Convert to Grayscale)
        logger.info(f"Processing image {target_image_name}...")
        img = Image.open(img_path)
        
        # Ensure it's RGB so grayscale works consistently, then convert to grayscale
        if img.mode != 'RGB':
            img = img.convert('RGB')
        gray_img = ImageOps.grayscale(img)
        
        # Save processed image (ensure we just use the basename to avoid subdirectory issues)
        base_name = os.path.basename(target_image_name)
        processed_path = os.path.join(extract_dir, f"processed_{base_name}")
        gray_img.save(processed_path)
        
        # Simulate some heavy compute time
        time.sleep(2)
        
        # 5. Upload the result back to MinIO
        result_object_name = f"{job_id}/results/{task_id}_{base_name}"
        result_url = storage.upload_result(bucket, processed_path, result_object_name)
        
        logger.info(f"[ImageStrategy] Task {task_id} complete. Result at {result_url}")
        
        return {
            "task_id": task_id,
            "status": "success",
            "result_url": result_url
        }
