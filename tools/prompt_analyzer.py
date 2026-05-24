import sys
import re
import argparse
from pathlib import Path

def analyze_prompt(file_path):
    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    score = 100
    suggestions = []
    
    # Check for Role/Persona
    if not re.search(r'(أنت|دورك|act as|you are|role)', content, re.IGNORECASE):
        score -= 15
        suggestions.append("- Missing Role/Persona: Define who the AI should act as (e.g., 'You are an expert...').")
        
    # Check for Task/Objective
    if not re.search(r'(مهمتك|المطلوب|أريد|هدف|task|objective|goal|want)', content, re.IGNORECASE):
        score -= 20
        suggestions.append("- Missing Task/Objective: Clearly state what you want the AI to do.")
        
    # Check for Context
    if not re.search(r'(سياق|خلفية|بسبب|لأن|context|background|since|because)', content, re.IGNORECASE):
        score -= 15
        suggestions.append("- Missing Context: Provide background information so the AI understands *why* you are doing this.")
        
    # Check for Constraints/Rules
    if not re.search(r'(قيود|شروط|تجنب|يجب|يمنع|لا تقم|constraints|rules|must|avoid|do not)', content, re.IGNORECASE):
        score -= 20
        suggestions.append("- Missing Constraints: Tell the AI what to avoid or what rules to strictly follow.")
        
    # Check for Output Format
    if not re.search(r'(تنسيق|شكل|جدول|قائمة|ماركداون|format|output|markdown|table|list|json)', content, re.IGNORECASE):
        score -= 15
        suggestions.append("- Missing Output Format: Specify exactly how you want the answer formatted.")
        
    # Check Length
    word_count = len(content.split())
    if word_count < 20:
        score -= 15
        suggestions.append("- Too Short: The prompt is too brief to provide high-quality context.")
        
    print("\n" + "="*50)
    print("🎯 PROMPT ANALYSIS REPORT")
    print("="*50)
    
    # Cap score at 100 and lowest at 0
    score = max(0, min(100, score))
    
    if score >= 90:
        print(f"⭐ Score: {score}/100 - EXCELLENT!")
    elif score >= 70:
        print(f"👍 Score: {score}/100 - GOOD (Needs some tweaks)")
    else:
        print(f"⚠️ Score: {score}/100 - WEAK (Needs major improvements)")
        
    if suggestions:
        print("\n💡 Suggestions to reach 100/100:")
        for s in suggestions:
            print(s)
    else:
        print("\n💡 Your prompt is perfect! No suggestions needed.")
        
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a prompt file and score it out of 100.")
    parser.add_argument("file", help="Path to the markdown or text file containing the prompt")
    args = parser.parse_args()
    
    analyze_prompt(args.file)
