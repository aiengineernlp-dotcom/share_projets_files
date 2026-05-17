from PIL import Image

# Load the uploaded image
image_path = "/mnt/data/Home_ResearchConsulting_AdobeStock_404757410.jpeg"
img = Image.open(image_path)

# Resize to 2560x1350
resized_img = img.resize((2560, 1350), Image.LANCZOS)

# Save the resized image
resized_path = "/mnt/data/Home_ResearchConsulting_Resized_2560x1350.jpeg"
resized_img.save(resized_path)

resized_path


# STDOUT/STDERR
# /tmp/ipykernel_12/1073676668.py:8: DeprecationWarning: LANCZOS is deprecated and will be removed in Pillow 10 (2023-07-01). Use Resampling.LANCZOS instead.
#   resized_img = img.resize((2560, 1350), Image.LANCZOS)
# Result
# '/mnt/data/Home_ResearchConsulting_Resized_2560x1350.jpeg'