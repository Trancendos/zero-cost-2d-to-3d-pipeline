#!/bin/bash
# One-click pipeline for Cornelius MacIntyre
# Usage: bash characters/cornelius/run_cornelius_pipeline.sh

set -e

echo "=== Cornelius MacIntyre Pipeline ==="

# Check we are in the right place
if [ ! -f "multi_image_to_3d.py" ]; then
  echo "Error: Please run this script from the root of the zero-cost-2d-to-3d-pipeline repository."
  exit 1
fi

INPUT="examples/cornelius_macintyre.png"
OUT_DIR="output/cornelius"
mkdir -p "$OUT_DIR"

echo ""
echo "[1/3] Generating 3D mesh with TripoSR..."
python multi_image_to_3d.py "$INPUT" --out "$OUT_DIR" --res 320

MESH="$OUT_DIR/cornelius_macintyre.glb"

if [ ! -f "$MESH" ]; then
  echo "Error: Mesh generation failed."
  exit 1
fi

echo ""
echo "[2/3] Cleaning mesh + creating UVs..."
blender --background --python blender_cleanup_rig.py -- \
  "$MESH" \
  "$OUT_DIR/cornelius_cleaned.glb"

echo ""
echo "[3/3] Creating cleaned version with basic armature..."
blender --background --python blender_cleanup_rig.py -- \
  "$MESH" \
  "$OUT_DIR/cornelius_rigged.glb" --rig

echo ""
echo "✅ Done!"
echo "Generated files:"
echo "  - $OUT_DIR/cornelius_macintyre.glb     (raw)"
echo "  - $OUT_DIR/cornelius_cleaned.glb       (cleaned + UVs)"
echo "  - $OUT_DIR/cornelius_rigged.glb        (cleaned + basic rig)"
echo ""
echo "Next recommended steps:"
echo "  1. Improve auto-rig with SkinTokens or AssetFurnace if possible"
echo "  2. Convert the best version to VRM using the Blender VRM add-on"
echo "  3. Use characters/cornelius/personality.txt with Ollama or the talking launcher"
