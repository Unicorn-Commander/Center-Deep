from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('static/images', exist_ok=True)

# Create Center Deep logo placeholder (astronaut unicorn)
img = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a circle for the helmet
draw.ellipse([50, 50, 250, 250], fill=(0, 188, 212, 100), outline=(0, 188, 212, 255), width=3)

# Draw unicorn horn
points = [(150, 50), (130, 100), (170, 100)]
draw.polygon(points, fill=(255, 193, 7, 255))

# Add some stars
for i in range(5):
    x, y = 70 + i * 40, 220
    draw.ellipse([x-3, y-3, x+3, y+3], fill=(255, 255, 255, 200))

img.save('static/images/center-deep-logo.png')
print("Created center-deep-logo.png")

# Create Magic Unicorn logo placeholder
img2 = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
draw2 = ImageDraw.Draw(img2)

# Draw unicorn shape
draw2.ellipse([50, 50, 150, 150], fill=(218, 112, 214, 255))
# Horn
points2 = [(100, 30), (90, 70), (110, 70)]
draw2.polygon(points2, fill=(147, 112, 219, 255))

img2.save('static/images/magic-unicorn-logo.png')
print("Created magic-unicorn-logo.png")

# Create Unicorn Commander logo placeholder
img3 = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
draw3 = ImageDraw.Draw(img3)

# Draw beret
draw3.ellipse([40, 30, 160, 80], fill=(0, 0, 139, 255))
# Draw unicorn head
draw3.ellipse([50, 60, 150, 160], fill=(240, 240, 240, 255))
# Horn
points3 = [(100, 40), (90, 80), (110, 80)]
draw3.polygon(points3, fill=(255, 215, 0, 255))

img3.save('static/images/unicorn-commander-logo.png')
print("Created unicorn-commander-logo.png")