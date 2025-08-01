from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple favicon
size = 32
img = Image.new('RGB', (size, size), color='#2c3e50')
draw = ImageDraw.Draw(img)

# Draw a simple "CD" text
try:
    # Try to use a system font
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
except:
    # Fallback to default font
    font = ImageFont.load_default()

# Draw text
draw.text((4, 4), "CD", fill='white', font=font)

# Save as favicon
os.makedirs('static', exist_ok=True)
img.save('static/favicon.ico', format='ICO')
print("Favicon created successfully!")