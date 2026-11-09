from PIL import Image, ImageDraw
from pathlib import Path

icons_dir = Path("chrome-extension/icons")
icons_dir.mkdir(parents=True, exist_ok=True)

for size in [16, 48, 128]:
    img = Image.new("RGBA", (size, size), (12, 14, 20, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer circular glow
    pad = max(1, size // 10)
    draw.ellipse([pad, pad, size - pad, size - pad], fill=(25, 20, 22, 255), outline=(255, 92, 0, 255), width=max(1, size // 16))
    
    # Orange cursor arrow triangle
    cx, cy = size / 2, size / 2
    s = size / 3
    points = [
        (cx - s * 0.7, cy - s * 0.9),
        (cx + s * 0.8, cy + s * 0.1),
        (cx - s * 0.2, cy + s * 0.9),
    ]
    draw.polygon(points, fill=(255, 92, 0, 255))
    
    # Center dot
    dot_r = max(1, size // 14)
    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=(255, 255, 255, 255))
    
    img.save(icons_dir / f"icon{size}.png")
    print(f"Generated icon{size}.png")
