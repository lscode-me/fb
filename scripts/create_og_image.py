#!/usr/bin/env python3
"""Generate OG image for fb.lscode.me"""

from PIL import Image, ImageDraw, ImageFont
import os

# Image dimensions (recommended for OG)
WIDTH = 1200
HEIGHT = 630

# Colors
BG_COLOR = (26, 32, 44)        # Dark blue-gray
ACCENT_COLOR = (99, 179, 237)  # Light blue
TEXT_COLOR = (255, 255, 255)   # White
SUBTITLE_COLOR = (160, 174, 192)  # Gray

def create_og_image():
    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw decorative elements - file icons pattern
    icon_color = (45, 55, 72)  # Slightly lighter than BG
    
    # Draw grid of file icons in background
    for x in range(0, WIDTH, 80):
        for y in range(0, HEIGHT, 80):
            offset = (y // 80) % 2 * 40  # Stagger pattern
            draw.rectangle([x + offset + 10, y + 10, x + offset + 50, y + 60], 
                          outline=icon_color, width=2)
            draw.rectangle([x + offset + 10, y + 10, x + offset + 30, y + 20], 
                          fill=icon_color)
    
    # Draw accent gradient bar at top
    for i in range(8):
        alpha = 255 - i * 30
        color = (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2])
        draw.rectangle([0, i * 2, WIDTH, i * 2 + 2], fill=color)
    
    # Draw main content area with semi-transparent overlay
    overlay_padding = 60
    draw.rectangle(
        [overlay_padding, 150, WIDTH - overlay_padding, HEIGHT - 100],
        fill=(37, 47, 63)
    )
    
    # Try to load system fonts (fallback to default)
    try:
        # macOS fonts
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        emoji_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            emoji_font = subtitle_font
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            emoji_font = subtitle_font
    
    # Draw title
    title = "Файлы: missing manual"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2
    draw.text((title_x, 200), title, font=title_font, fill=TEXT_COLOR)
    
    # Draw subtitle line 1
    subtitle1 = "Полное руководство по файлам и форматам"
    sub1_bbox = draw.textbbox((0, 0), subtitle1, font=subtitle_font)
    sub1_width = sub1_bbox[2] - sub1_bbox[0]
    sub1_x = (WIDTH - sub1_width) // 2
    draw.text((sub1_x, 310), subtitle1, font=subtitle_font, fill=SUBTITLE_COLOR)
    
    # Draw subtitle line 2
    subtitle2 = "От байтов до терабайтов"
    sub2_bbox = draw.textbbox((0, 0), subtitle2, font=subtitle_font)
    sub2_width = sub2_bbox[2] - sub2_bbox[0]
    sub2_x = (WIDTH - sub2_width) // 2
    draw.text((sub2_x, 360), subtitle2, font=subtitle_font, fill=ACCENT_COLOR)
    
    # Draw tags/keywords
    tags = ["JSON", "YAML", "UTF-8", "Linux", "Python", "ZFS"]
    tag_font = subtitle_font
    tag_y = 440
    
    # Calculate total width
    tag_widths = []
    spacing = 30
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=tag_font)
        tag_widths.append(bbox[2] - bbox[0] + 40)  # padding
    
    total_width = sum(tag_widths) + spacing * (len(tags) - 1)
    tag_x = (WIDTH - total_width) // 2
    
    for i, tag in enumerate(tags):
        tag_width = tag_widths[i]
        # Draw tag background
        draw.rounded_rectangle(
            [tag_x, tag_y, tag_x + tag_width, tag_y + 45],
            radius=8,
            fill=(55, 65, 81)
        )
        # Draw tag text
        text_bbox = draw.textbbox((0, 0), tag, font=tag_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = tag_x + (tag_width - text_width) // 2
        draw.text((text_x, tag_y + 6), tag, font=tag_font, fill=ACCENT_COLOR)
        tag_x += tag_width + spacing
    
    # Draw URL at bottom
    url = "fb.lscode.me"
    url_bbox = draw.textbbox((0, 0), url, font=subtitle_font)
    url_width = url_bbox[2] - url_bbox[0]
    url_x = (WIDTH - url_width) // 2
    draw.text((url_x, HEIGHT - 70), url, font=subtitle_font, fill=SUBTITLE_COLOR)
    
    # Draw accent line at bottom
    draw.rectangle([100, HEIGHT - 20, WIDTH - 100, HEIGHT - 16], fill=ACCENT_COLOR)
    
    return img

if __name__ == "__main__":
    img = create_og_image()
    output_path = os.path.join(os.path.dirname(__file__), 
                               "../docs/assets/images/og-image.png")
    img.save(output_path, "PNG", quality=95)
    print(f"OG image saved to: {output_path}")
    print(f"Size: {img.size}")
