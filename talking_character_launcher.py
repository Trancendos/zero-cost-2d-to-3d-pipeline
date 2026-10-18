#!/usr/bin/env python3
"""
Simple Talking Character Launcher (Starter)
------------------------------------------
This is a practical starting point, not a full production system.

It assumes you already have:
- A rigged / VRM-ready model (or at least a GLB)
- Ollama running locally with a model (e.g. llama3.1, qwen2.5)
- Optional: a TTS engine (Piper / Kokoro etc.)

For a real interactive avatar you will still need a frontend
(Three.js + VRM or an existing framework like Amica / AITuber Kit).
"""

import subprocess
import sys
import os
from pathlib import Path

def check_ollama():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is available")
            print(result.stdout[:500])
            return True
    except FileNotFoundError:
        print("❌ Ollama not found. Install from https://ollama.com and pull a model:")
        print("   ollama pull llama3.1")
    return False

def main():
    print("=== Talking Character Launcher (Starter) ===\n")
    
    model_path = input("Path to your GLB / VRM model (or press Enter to skip): ").strip()
    if model_path and not Path(model_path).exists():
        print(f"Warning: {model_path} not found")
    
    print("\n1. Checking local LLM (Ollama)...")
    has_ollama = check_ollama()
    
    print("\n2. Recommended next steps for a real talking character:")
    print("   - Convert your model to VRM (Blender VRM add-on)")
    print("   - Use one of these open frameworks:")
    print("       • Amica")
    print("       • AITuber Kit")
    print("       • Custom Three.js + @pixiv/three-vrm + Whisper + Ollama + TTS")
    print("   - For lip-sync: map TTS visemes to VRM blendshapes")
    
    if has_ollama:
        print("\n3. Quick test conversation with Ollama:")
        personality = input("Character personality prompt (or Enter for default): ").strip()
        if not personality:
            personality = "You are a friendly 3D character assistant. Keep answers short and warm."
        
        print("\nStarting simple chat (type 'quit' to exit)...")
        while True:
            user = input("\nYou: ").strip()
            if user.lower() in ["quit", "exit"]:
                break
            try:
                result = subprocess.run(
                    ["ollama", "run", "llama3.1", f"{personality}\n\nUser: {user}\nAssistant:"],
                    capture_output=True, text=True, timeout=60
                )
                print("Character:", result.stdout.strip()[:1000])
            except Exception as e:
                print("Error:", e)
                break
    
    print("\nLauncher finished. For a full visual talking avatar, combine this with a VRM frontend.")

if __name__ == "__main__":
    main()
