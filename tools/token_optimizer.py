import sys
import argparse
from pathlib import Path
try:
    import tiktoken
except ImportError:
    print("Please install tiktoken: pip install tiktoken")
    sys.exit(1)

def optimize_tokens(file_path):
    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Initialize tokenizer (using cl100k_base which is used by GPT-3.5/4)
    encoding = tiktoken.get_encoding("cl100k_base")
    
    original_tokens = len(encoding.encode(content))
    
    # Basic optimization: Remove multiple spaces, newlines, and trailing spaces
    import re
    optimized_content = re.sub(r' +', ' ', content)
    optimized_content = re.sub(r'\n{3,}', '\n\n', optimized_content)
    optimized_content = optimized_content.strip()
    
    optimized_tokens = len(encoding.encode(optimized_content))
    saved_tokens = original_tokens - optimized_tokens
    
    print("\n" + "="*50)
    print("📉 TOKEN OPTIMIZER REPORT")
    print("="*50)
    print(f"Original Tokens : {original_tokens}")
    print(f"Optimized Tokens: {optimized_tokens}")
    print(f"Tokens Saved    : {saved_tokens} ({((saved_tokens)/original_tokens)*100 if original_tokens else 0:.1f}%)")
    print("="*50)
    
    if saved_tokens > 0:
        save_path = Path(file_path).with_suffix('.optimized' + Path(file_path).suffix)
        save_path.write_text(optimized_content, encoding='utf-8')
        print(f"\n✅ Saved optimized prompt to: {save_path.name}")
    else:
        print("\n✅ Prompt is already token-optimized! No extra spaces found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and optimize tokens for a prompt.")
    parser.add_argument("file", help="Path to the markdown or text file")
    args = parser.parse_args()
    
    optimize_tokens(args.file)
