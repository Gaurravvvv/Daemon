import os
import zipfile
from PIL import Image, ImageDraw
import random

def generate_test_images():
    print("Generating Test Dataset (10 Images)...")
    os.makedirs("test_data", exist_ok=True)
    
    # Generate 10 simple colorful images
    image_files = []
    for i in range(10):
        # Create a solid color image
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        img = Image.new('RGB', (800, 600), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add some text/shapes so it's not totally blank
        draw.rectangle([100, 100, 700, 500], outline="black", width=5)
        
        filename = f"test_data/image_{i}.jpg"
        img.save(filename)
        image_files.append(filename)
        print(f"Created {filename}")
        
    print("Packaging into payload.zip...")
    with zipfile.ZipFile("payload.zip", "w") as zf:
        for f in image_files:
            # Arcname ensures it just goes in root of zip
            zf.write(f, arcname=os.path.basename(f))
            
    print("Done! You can now upload payload.zip via the DaeMon Dashboard.")

if __name__ == "__main__":
    generate_test_images()
