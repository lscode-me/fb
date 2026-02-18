#!/usr/bin/env python3
"""Generate favicon for fb.lscode.me"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    bg_color = (99, 179, 237)  # Light blue (accent)
    fold_color = (66, 153, 225)  # Darker blue for fold
    text_color = (255, 255, 255)  # White
    
    # Calculate proportions
    margin = size // 8
    fold_size = size // 4
    
    # Draw file shape with folded corner
    points = [
        (margin, margin),
        (size - margin - fold_size, margin),
        (size - margin, margin + fold_size),
        (size - margin, size - margin),
        (margin, size - margin),
    ]
    draw.polygon(points, fill=bg_color)
    
    # Draw fold
    fold_points = [
        (size - margin - fold_size, margin),
        (size - margin - fold_size, margin + fold_size),
        (size - margin, margin + fold_size),
    ]
    draw.polygon(fold_points, fill=fold_color)
    
    # Draw "F" letter
    try:
        font_size = int(size * 0.5)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    letter = "F"
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - bbox[1] + size // 16
    draw.text((text_x, text_y), letter, font=font, fill=text_color)
    
    return img

if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "../docs/assets/images")
    os.makedirs(output_dir, exist_ok=True)

    # Generate different sizes
    favicon_16 = create_favicon(16)
    favicon_32 = create_favicon(32)

    # Save as ICO
    favicon_32.save(f"{output_dir}/favicon.ico", format='ICO')

    # Save individual PNGs
    create_favicon(32).save(f"{output_dir}/favicon-32x32.png")
    create_favicon(16).save(f"{output_dir}/favicon-16x16.png")
    create_favicon(180).save(f"{output_dir}/apple-touch-icon.png")
    create_favicon(192).save(f"{output_dir}/android-chrome-192x192.png")
    create_favicon(512).save(f"{output_dir}/android-chrome-512x512.png")

    print("Favicons created:")
    for f in sorted(os.listdir(output_dir)):
        if 'favicon' in f or 'apple' in f or 'android' in f:
            path = f"{output_dir}/{f}"
            print(f"  {f}: {os.path.getsize(path)} bytes")
