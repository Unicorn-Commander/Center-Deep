from PIL import Image
import os

# Open the Center Deep logo
logo = Image.open('static/images/center-deep-logo.png')

# Convert to RGBA if needed
if logo.mode != 'RGBA':
    logo = logo.convert('RGBA')

# Create multiple sizes for favicon
sizes = [(16, 16), (32, 32), (48, 48)]
favicon_images = []

for size in sizes:
    # Resize with high quality
    resized = logo.resize(size, Image.Resampling.LANCZOS)
    favicon_images.append(resized)

# Save as ICO with multiple sizes
favicon_images[0].save('static/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)], append_images=favicon_images[1:])
print("Created favicon.ico from Center Deep logo")