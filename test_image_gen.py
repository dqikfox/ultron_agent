import os
from PIL import Image, ImageDraw, ImageFont
import time

# Create output directory
output_dir = r'C:\Users\ultro\OneDrive\Pictures\STABLED'
os.makedirs(output_dir, exist_ok=True)

# Create a test image
width, height = 512, 512
image = Image.new('RGB', (width, height), color='lightblue')
draw = ImageDraw.Draw(image)

# Add some text
try:
    font = ImageFont.truetype('arial.ttf', 20)
except:
    font = ImageFont.load_default()

text = 'ULTRON Test Image\nGenerated at: ' + time.strftime('%Y-%m-%d %H:%M:%S')
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (width - text_width) // 2
y = (height - text_height) // 2

draw.text((x, y), text, fill='black', font=font)

# Save the image
timestamp = int(time.time())
filename = f'ultron_test_{timestamp}.png'
filepath = os.path.join(output_dir, filename)
image.save(filepath)

print(f'✅ Test image created successfully!')
print(f'📁 Saved to: {filepath}')
print(f'📏 Size: {width}x{height} pixels')
print(f'🖼️  Total images in directory: {len(os.listdir(output_dir))}')

# List all files in the directory
print('\n📂 Files in STABLED directory:')
for file in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file)
    size = os.path.getsize(file_path)
    print(f'  - {file} ({size} bytes)')
