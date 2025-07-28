#!/usr/bin/env python3
"""
Create favicon for ULTRON interface
Generates a simple ULTRON-themed favicon
"""

import os
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_simple_favicon():
    """Create a simple favicon without PIL using ASCII art approach"""
    # Create a simple HTML-based favicon (data URL)
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
    <defs>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#00FF41;stop-opacity:1" />
            <stop offset="70%" style="stop-color:#00AA22;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#004411;stop-opacity:0.3" />
        </radialGradient>
    </defs>
    <rect width="32" height="32" fill="#000000"/>
    <circle cx="16" cy="16" r="12" fill="url(#glow)" stroke="#00FF41" stroke-width="1"/>
    <text x="16" y="20" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle" fill="#000000">U</text>
</svg>'''
    
    return svg_content

def create_favicon_with_pil():
    """Create favicon using PIL"""
    # Create 32x32 image
    size = (32, 32)
    img = Image.new('RGBA', size, (0, 0, 0, 255))  # Black background
    draw = ImageDraw.Draw(img)
    
    # Draw glowing circle
    center = (16, 16)
    radius = 12
    
    # Create glow effect with multiple circles
    for i in range(radius, 0, -1):
        alpha = int(255 * (radius - i) / radius * 0.8)
        color = (0, 255, 65, alpha)
        draw.ellipse([center[0]-i, center[1]-i, center[0]+i, center[1]+i], fill=color)
    
    # Draw main circle
    draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], 
                 outline=(0, 255, 65, 255), width=2)
    
    # Try to add text (U for ULTRON)
    try:
        # Use default font
        font_size = 16
        draw.text((center[0], center[1]-2), "U", fill=(0, 0, 0, 255), anchor="mm")
    except:
        # Fallback - just draw a simple shape
        draw.rectangle([center[0]-3, center[1]-6, center[0]+3, center[1]+6], fill=(0, 0, 0, 255))
    
    return img

def main():
    """Create favicon files"""
    print("Creating ULTRON favicon...")
    
    assets_dir = os.path.dirname(__file__)
    
    if PIL_AVAILABLE:
        try:
            # Create PNG favicon with PIL
            img = create_favicon_with_pil()
            
            # Save as PNG
            png_path = os.path.join(assets_dir, 'favicon.png')
            img.save(png_path, 'PNG')
            print(f"Created: favicon.png")
            
            # Save as ICO
            ico_path = os.path.join(assets_dir, 'favicon.ico')
            img.save(ico_path, 'ICO', sizes=[(32, 32), (16, 16)])
            print(f"Created: favicon.ico")
            
        except Exception as e:
            print(f"PIL creation failed: {e}")
            create_fallback_favicon(assets_dir)
    else:
        print("PIL not available, creating SVG favicon...")
        create_fallback_favicon(assets_dir)

def create_fallback_favicon(assets_dir):
    """Create a simple fallback favicon"""
    # Create SVG favicon
    svg_content = create_simple_favicon()
    svg_path = os.path.join(assets_dir, 'favicon.svg')
    
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    print(f"Created: favicon.svg")
    
    # Create a simple 32x32 bitmap manually for ICO
    # This is a very basic approach
    try:
        if PIL_AVAILABLE:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (32, 32), (0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Simple green circle
            draw.ellipse([8, 8, 24, 24], fill=(0, 255, 65), outline=(0, 200, 50))
            
            # Save as ICO
            ico_path = os.path.join(assets_dir, 'favicon.ico')
            img.save(ico_path, 'ICO', sizes=[(32, 32)])
            print(f"Created: favicon.ico (simple)")
            
            # Save as PNG too
            png_path = os.path.join(assets_dir, 'favicon.png')
            img.save(png_path, 'PNG')
            print(f"Created: favicon.png (simple)")
            
    except Exception as e:
        print(f"Fallback favicon creation failed: {e}")
        print("Manual favicon creation required")

if __name__ == "__main__":
    main()
