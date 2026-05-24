import sys
import json
from pathlib import Path

def print_header():
    print("="*60)
    print("🤖 INTERACTIVE PROMPT ENGINEER (Local CLI)")
    print("="*60)
    print("Welcome! I will ask you a few questions to build a 100/100 prompt.\n")

def main():
    print_header()
    
    # State tracking
    state = {
        "role": "",
        "task": "",
        "audience": "",
        "format": "",
        "constraints": []
    }
    
    # 1. Role
    print("1️⃣  Who should the AI act as? (e.g., 'Senior Python Developer', 'Marketing Expert')")
    state["role"] = input("> ").strip() or "Helpful Assistant"
    
    # 2. Task
    print("\n2️⃣  What is the main task or objective? (Be specific)")
    state["task"] = input("> ").strip()
    if not state["task"]:
        print("Task is required! Exiting...")
        sys.exit(1)
        
    # 3. Audience
    print("\n3️⃣  Who is the target audience for the output? (e.g., 'Beginners', 'Management')")
    state["audience"] = input("> ").strip() or "General Audience"
    
    # 4. Format
    print("\n4️⃣  What format do you want? (e.g., 'Markdown table', 'Bullet points', 'JSON')")
    state["format"] = input("> ").strip() or "Clear text with headings"
    
    # 5. Constraints
    print("\n5️⃣  Any constraints or things to AVOID? (Comma separated, e.g., 'No jargon, keep it under 500 words')")
    constraints_input = input("> ").strip()
    if constraints_input:
        state["constraints"] = [c.strip() for c in constraints_input.split(',')]
        
    # Generate Prompt
    print("\n" + "="*60)
    print("✨ GENERATING YOUR PERFECT PROMPT ✨")
    print("="*60)
    
    final_prompt = f"""# Role
You are an expert {state["role"]}.

# Task
Your objective is to: {state["task"]}

# Target Audience
Tailor your response for: {state["audience"]}

# Constraints & Rules
Please strictly follow these rules:
"""
    if state["constraints"]:
        for c in state["constraints"]:
            final_prompt += f"- {c}\n"
    else:
        final_prompt += "- Provide accurate and high-quality information.\n"
        
    final_prompt += f"""
# Output Format
Present your response in the following format:
{state["format"]}
"""

    print("\n" + final_prompt)
    print("="*60)
    
    # Save to file
    save = input("\nDo you want to save this prompt to a file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Enter filename (e.g., my_prompt.md): ").strip()
        if not filename.endswith('.md') and not filename.endswith('.txt'):
            filename += '.md'
        
        save_path = Path.cwd() / filename
        save_path.write_text(final_prompt, encoding='utf-8')
        print(f"✅ Prompt saved successfully to {save_path.resolve()}")
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted. Goodbye!")
        sys.exit(0)
