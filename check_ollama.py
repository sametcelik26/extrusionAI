import sys
import httpx
import requests
import asyncio

def check_ollama():
    try:
        response = requests.get('http://localhost:11434/')
        if response.status_code == 200:
            print("[OK] Ollama server is running.")
            return True
    except requests.exceptions.ConnectionError:
        pass
    
    print("\n" + "="*60)
    print(" ⚠️  WARNING: Ollama server is NOT running!")
    print("="*60)
    print("ExtrusionAI requires Ollama to analyze problems with AI.")
    print("The system will fall back to basic database matching.")
    print("\nTo enable full AI features:")
    print("1. Install Ollama from: https://ollama.ai/")
    print("2. Run the models used by ExtrusionAI:")
    print("   ollama run llama3")
    print("   ollama run llava")
    print("="*60 + "\n")
    return False

if __name__ == "__main__":
    check_ollama()
