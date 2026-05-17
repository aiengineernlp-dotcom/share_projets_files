from PIL import Image
import os

# Paths to the uploaded files
image_paths = [
    "/mnt/data/ResearchConsulting_Concept_Blub_AdobeStock_354237195 2 (1).jpeg",
    "/mnt/data/ResearchConsulting_freepik__upload__47457 2 (1).jpeg"
]

# Output directory
output_dir = "/mnt/data/compressed_images"
os.makedirs(output_dir, exist_ok=True)

# Function to compress an image
def compress_image(input_path, output_path, quality=20):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.save(output_path, "JPEG", optimize=True, quality=quality)

# Compress each image
compressed_paths = []
for path in image_paths:
    filename = os.path.basename(path).replace(" ", "_")
    compressed_path = os.path.join(output_dir, f"compressed_{filename}")
    compress_image(path, compressed_path)
    compressed_paths.append(compressed_path)

compressed_paths
