import zipfile
import re
import os
import shutil
from PIL import Image

def update_docx_image(docx_path, new_image_path):
    if not os.path.exists(docx_path):
        print(f"File not found: {docx_path}")
        return

    # Get dimensions of new image
    with Image.open(new_image_path) as img:
        img_w, img_h = img.size
    aspect_ratio = img_h / img_w

    # Standard Word page text width: 6.6 inches = 6.6 * 914400 EMUs = 6035040 EMUs
    # Or keep original cx and scale cy proportionally
    with open(new_image_path, "rb") as f:
        new_image_bytes = f.read()

    temp_docx = docx_path + ".tmp"
    with zipfile.ZipFile(docx_path, "r") as zin:
        with zipfile.ZipFile(temp_docx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/media/image1.png":
                    zout.writestr(item, new_image_bytes)
                elif item.filename == "word/document.xml":
                    xml_str = zin.read(item.filename).decode("utf-8")
                    
                    # Search for wp:extent and a:ext
                    # Example: <wp:extent cx="6035040" cy="3269220"/>
                    def replace_extent(match):
                        cx = int(match.group(1))
                        # Compute new cy based on aspect ratio
                        new_cy = int(cx * aspect_ratio)
                        return f'<wp:extent cx="{cx}" cy="{new_cy}"'
                    
                    def replace_aext(match):
                        cx = int(match.group(1))
                        new_cy = int(cx * aspect_ratio)
                        return f'<a:ext cx="{cx}" cy="{new_cy}"'

                    xml_str = re.sub(r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"', replace_extent, xml_str)
                    xml_str = re.sub(r'<a:ext\s+cx="(\d+)"\s+cy="(\d+)"', replace_aext, xml_str)

                    zout.writestr(item, xml_str.encode("utf-8"))
                else:
                    zout.writestr(item, zin.read(item.filename))

    shutil.move(temp_docx, docx_path)
    print(f"Successfully replaced diagram in: {docx_path}")

if __name__ == "__main__":
    survey_dir = r"c:\Users\VICTUS\OneDrive\Desktop\4th Year Project\DaeMon\survey paper"
    new_img = os.path.join(survey_dir, "architecture_diagram_colorful.png")
    dst_img = os.path.join(survey_dir, "architecture_diagram.png")
    
    # 1. Overwrite architecture_diagram.png so any rebuild script uses the new image
    shutil.copy2(new_img, dst_img)
    print(f"Copied {new_img} -> {dst_img}")

    # 2. Update docx files directly
    for fname in ["DaeMon_Survey_Paper.docx", "DaeMon_Survey_Paper_Updated.docx"]:
        fpath = os.path.join(survey_dir, fname)
        if os.path.exists(fpath):
            update_docx_image(fpath, new_img)
