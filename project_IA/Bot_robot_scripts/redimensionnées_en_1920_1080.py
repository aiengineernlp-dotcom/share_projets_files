from PIL import Image

# Define the paths to the uploaded files
image1_path = "/mnt/data/breast-cancer-awareness-scaled.webp"
image2_path = "/mnt/data/ChatGPT Image Oct 8, 2025, 07_07_46 AM.png"

# Open the images
image1 = Image.open(image1_path)
image2 = Image.open(image2_path)

# Resize both images to 1920x1080
size = (1920, 1080)
image1_resized = image1.resize(size, Image.LANCZOS)
image2_resized = image2.resize(size, Image.LANCZOS)

# Save the resized images
image1_output_path = "/mnt/data/breast-cancer-awareness-1920x1080.webp"
image2_output_path = "/mnt/data/tkh-anniversary-1920x1080.png"

image1_resized.save(image1_output_path)
image2_resized.save(image2_output_path)

(image1_output_path, image2_output_path)

