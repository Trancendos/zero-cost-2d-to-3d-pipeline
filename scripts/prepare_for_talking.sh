#!/bin/bash
# One-click reminder + helper for preparing a character for talking
# Usage: bash scripts/prepare_for_talking.sh cornelius

CHARACTER=${1:-cornelius}

echo "=== Prepare $CHARACTER for Talking ==="
echo ""
echo "1. Make sure you have a cleaned + rigged GLB"
echo "2. Convert it to VRM using the Blender VRM add-on (see docs/vrm_conversion_guide.md)"
echo "3. Place the .vrm file in characters/$CHARACTER/ if you want"
echo ""
echo "Then you can talk to the character with:"
echo "  python scripts/talk_with_character.py $CHARACTER"
echo ""
echo "For a full visual avatar you still need a frontend such as:"
echo "  - Amica"
echo "  - AITuber Kit"
echo "  - Three.js + @pixiv/three-vrm"
echo ""
echo "Personality file location:"
echo "  characters/$CHARACTER/personality.txt"
