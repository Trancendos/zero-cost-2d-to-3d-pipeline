#!/usr/bin/env python3
"""
Zero-cost Multi-Model 2D → 3D Pipeline
Primary: TripoSR (low VRAM)
Fallback / High quality: TRELLIS.2 (if available & enough VRAM)
"""

import os
import sys
import argparse
from pathlib import Path
import torch
from PIL import Image
from rembg import remove
import trimesh

def run_triposr(img: Image.Image, resolution: int = 256, device: str = "cuda"):
    sys.path.append(str(Path(__file__).parent / "TripoSR"))
    from tsr.system import TSR
    from tsr.utils import resize_foreground

    img = resize_foreground(img, 0.85)
    model = TSR.from_pretrained("stabilityai/TripoSR", config_name="config.yaml", weight_name="model.ckpt")
    model.renderer.chunk_size = 8192
    model.to(device)

    with torch.no_grad():
        scene_codes = model([img], device=device)
        meshes = model.extract_mesh(scene_codes, resolution=resolution)
    return meshes[0]

def main():
    parser = argparse.ArgumentParser(description="Multi-model Image to 3D")
    parser.add_argument("image", help="Input image")
    parser.add_argument("--out", default="output", help="Output folder")
    parser.add_argument("--model", choices=["triposr", "trellis2", "auto"], default="auto")
    parser.add_argument("--res", type=int, default=320)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    name = Path(args.image).stem
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading and cleaning image...")
    img = Image.open(args.image).convert("RGB")
    img = remove(img)

    mesh = None
    if args.model in ["triposr", "auto"]:
        print("Running TripoSR...")
        try:
            mesh = run_triposr(img, resolution=args.res, device=device)
        except Exception as e:
            print(f"TripoSR failed: {e}")

    if mesh is None and args.model in ["trellis2", "auto"]:
        print("TRELLIS.2 fallback requested. Please run official TRELLIS.2 inference and place the GLB in the output folder.")
        # Placeholder for full integration

    if mesh is None:
        print("No model succeeded.")
        return

    out_path = out_dir / f"{name}.glb"
    mesh.export(str(out_path))
    print(f"✅ Saved: {out_path}")
    print(f"   Vertices: {len(mesh.vertices):,}  |  Faces: {len(mesh.faces):,}")

if __name__ == "__main__":
    main()
