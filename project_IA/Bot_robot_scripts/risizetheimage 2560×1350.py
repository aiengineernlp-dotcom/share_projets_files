from PIL import Image

# je veux ces deux image en 2560 by 1350 pixels, compreseer et convertis en webp
from PIL import Image
import os

input_path = "/mnt/data/Our values shape everything we do.jpg"
output_path = "/mnt/data/output_image.webp"

# Load
img = Image.open(input_path)

# Resize to 2560x1350
img_resized = img.resize((2560, 1350))

# Save to WEBP with compression
img_resized.save(output_path, "WEBP", quality=80)

output_path
Result
'/mnt/data/output_image.webp'
