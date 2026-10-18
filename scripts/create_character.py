#!/usr/bin/env python3
"""
Create a new character folder from an image + short description.
Makes the pipeline smarter and more proactive.
"""

import argparse
import shutil
from pathlib import Path
import datetime

def create_character(image_path: str, name: str, description: str = ""):
    root = Path(__file__).parent.parent
    characters_dir = root / "characters"
    template_dir = characters_dir / "_template"
    
    # Clean name for folder
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower()).strip("_")
    char_dir = characters_dir / safe_name
    
    if char_dir.exists():
        print(f"Character folder already exists: {char_dir}")
        return
    
    char_dir.mkdir(parents=True)
    
    # Copy source image
    src = Path(image_path)
    if not src.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    dest_image = char_dir / "source.png"
    shutil.copy(src, dest_image)
    print(f"Copied image → {dest_image}")
    
    # Create personality file
    personality = f"""You are {name}, {description or 'a unique character'}.

Speak in a way that matches your character. Keep responses engaging, in-character, and concise unless the user asks for more detail.

Never break character.
"""
    (char_dir / "personality.txt").write_text(personality.strip() + "\n")
    print("Created personality.txt")
    
    # Create simple README
    readme = f"""# {name}

Created: {datetime.date.today()}

## Source
- Image: source.png

## Personality
See personality.txt

## Generate
```bash
python multi_image_to_3d.py characters/{safe_name}/source.png --out output/{safe_name} --res 320
```

Or use the one-click style script once adapted.
"""
    (char_dir / "README.md").write_text(readme)
    print(f"Created character folder: {char_dir}")
    print("Next: run the generation commands or adapt the pipeline script.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new character from an image")
    parser.add_argument("image", help="Path to the source image")
    parser.add_argument("--name", required=True, help="Character name")
    parser.add_argument("--description", default="", help="Short description for the personality")
    args = parser.parse_args()
    
    create_character(args.image, args.name, args.description)
