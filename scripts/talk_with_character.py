#!/usr/bin/env python3
"""
Simple Ollama + Personality Launcher
Talk to any character that has a personality.txt file.
"""

import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Talk to a character using Ollama")
    parser.add_argument("character", help="Character folder name (e.g. cornelius)")
    parser.add_argument("--model", default="llama3.1", help="Ollama model to use")
    args = parser.parse_args()
    
    root = Path(__file__).parent.parent
    personality_file = root / "characters" / args.character / "personality.txt"
    
    if not personality_file.exists():
        print(f"Personality file not found: {personality_file}")
        print("Available characters:")
        for d in (root / "characters").iterdir():
            if d.is_dir() and not d.name.startswith("_"):
                print(f"  - {d.name}")
        sys.exit(1)
    
    personality = personality_file.read_text().strip()
    
    print(f"=== Talking with {args.character} ===")
    print("Type 'quit' or 'exit' to stop.\n")
    
    # Check Ollama
    try:
        subprocess.run(["ollama", "list"], capture_output=True, check=True)
    except Exception:
        print("Ollama not found or not running. Install from https://ollama.com and pull a model.")
        sys.exit(1)
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
            
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye.")
            break
        if not user_input:
            continue
        
        prompt = f"{personality}\n\nUser: {user_input}\n{args.character}:"
        
        try:
            result = subprocess.run(
                ["ollama", "run", args.model, prompt],
                capture_output=True, text=True, timeout=90
            )
            response = result.stdout.strip()
            print(f"\n{args.character.capitalize()}: {response}\n")
        except subprocess.TimeoutExpired:
            print("Response timed out.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
