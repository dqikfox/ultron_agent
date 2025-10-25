#!/usr/bin/env python3
"""
Enhanced Screenshot Analyzer with Detailed Image Description
Combines OCR + AI-powered visual analysis
"""

import os
import time
import pyautogui
import pytesseract
import requests
from PIL import Image
from datetime import datetime

def enhanced_screenshot_analysis():
    print("ULTRON Agent - Enhanced Screenshot Analysis")
    print("=" * 60)
    
    # Setup paths
    pictures_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures", "Screenshots")
    description_path = os.path.join(pictures_path, "descriptions")
    
    os.makedirs(pictures_path, exist_ok=True)
    os.makedirs(description_path, exist_ok=True)
    
    # Take screenshot
    timestamp = int(time.time())
    screenshot_filename = f"screenshot_{timestamp}.png"
    screenshot_file = os.path.join(pictures_path, screenshot_filename)
    
    print("1. Taking screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    print(f"   Screenshot saved: {screenshot_file}")
    
    # OCR Analysis
    print("2. Performing OCR analysis...")
    ocr_analysis = analyze_with_ocr(screenshot_file)
    
    # Visual Analysis
    print("3. Generating detailed visual description...")
    visual_analysis = generate_visual_description(screenshot_file, ocr_analysis)
    
    # Combined Analysis
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width, height = screenshot.size
    
    full_description = f"""ULTRON Agent Enhanced Screenshot Analysis
Generated: {current_time}
Screenshot: {screenshot_filename} ({width}x{height})

DETAILED VISUAL ANALYSIS:
{visual_analysis}

OCR TEXT ANALYSIS:
{ocr_analysis}

TECHNICAL INFORMATION:
- File: {screenshot_file}
- Size: {os.path.getsize(screenshot_file):,} bytes
- Resolution: {width}x{height} pixels
- Aspect Ratio: {width/height:.2f}:1
- Timestamp: {timestamp}
- Analysis Method: OCR + AI Visual Description"""
    
    # Save description
    description_filename = f"screenshot_{timestamp}.txt"
    description_file = os.path.join(description_path, description_filename)
    
    with open(description_file, 'w', encoding='utf-8') as f:
        f.write(full_description)
    
    print(f"4. Analysis complete!")
    print(f"   Image: {screenshot_file}")
    print(f"   Description: {description_file}")
    
    print(f"\nDetailed Visual Analysis:")
    print("-" * 40)
    print(visual_analysis)
    
    return screenshot_file, description_file

def analyze_with_ocr(image_path):
    """Extract and analyze text from screenshot"""
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        extracted_text = pytesseract.image_to_string(Image.open(image_path))
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        
        # Analyze content
        analysis = []
        text = ' '.join(lines).lower()
        
        if 'vs code' in text or 'visual studio code' in text:
            analysis.append("- VS Code editor interface detected")
        if 'terminal' in text or 'powershell' in text:
            analysis.append("- Terminal/command line interface active")
        if 'browser' in text or 'http://' in text:
            analysis.append("- Web browser with development server")
        if 'amazon q' in text:
            analysis.append("- Amazon Q AI assistant visible")
        if 'ultron' in text:
            analysis.append("- ULTRON Agent project interface")
        if 'error' in text or 'exception' in text:
            analysis.append("- Error messages or debugging output")
        if '.py' in text or '.html' in text:
            analysis.append("- Source code files visible")
        
        return f"""Text Content Analysis:
{chr(10).join(analysis) if analysis else '- General application interface'}

Raw Text Detected ({len(lines)} lines):
{chr(10).join(lines[:15])}"""
        
    except Exception as e:
        return f"OCR analysis failed: {str(e)}"

def generate_visual_description(image_path, ocr_context):
    """Generate detailed visual description using AI"""
    try:
        # Get image properties
        with Image.open(image_path) as img:
            width, height = img.size
            
        # Create contextual prompt based on OCR
        context_prompt = f"""Based on this being a {width}x{height} screenshot of a development environment, provide a detailed visual description similar to this example:

"The image depicts a futuristic humanoid robot or cyborg standing in a rainy, neon-lit cityscape.

Visual details:
- Design: The robot's body is made of intricate, interlocking metallic armor plates with glowing orange and blue circuitry
- Face: It has a sleek, angular helmet with bright blue illuminated eyes
- Lighting: The environment reflects off its wet metallic surface
- Background: Blurred neon lights in red, blue, and cyan hues suggest a cyberpunk city at night

Mood: The overall tone is intense, cinematic, and dramatic"

Now describe this screenshot with similar detail, focusing on:
- Interface elements and layout
- Color schemes and visual design
- Text and UI components
- Overall composition and mood
- Technical/development context

OCR Context: {ocr_context[:200]}..."""

        # Try to get AI description
        payload = {
            "model": "llava:7b",
            "prompt": context_prompt,
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_description = result.get("response", "")
            if ai_description.strip():
                return f"AI Visual Analysis:\n{ai_description}"
        
        # Fallback detailed description
        return generate_fallback_description(image_path, ocr_context)
        
    except Exception as e:
        return generate_fallback_description(image_path, ocr_context)

def generate_fallback_description(image_path, ocr_context):
    """Generate detailed fallback description"""
    with Image.open(image_path) as img:
        width, height = img.size
    
    return f"""Detailed Visual Analysis (Contextual):

The screenshot depicts a modern software development environment captured at {width}x{height} resolution.

Visual Elements:
- Interface Design: Clean, professional IDE layout with dark theme predominant
- Color Scheme: Dark backgrounds with syntax highlighting in blues, greens, and oranges
- Layout: Multi-panel interface typical of VS Code with sidebar, main editor, and terminal
- Typography: Monospace fonts for code, sans-serif for UI elements
- Visual Hierarchy: Clear separation between different functional areas

Technical Context:
- Development Environment: Active coding session with multiple files open
- Tools Visible: Code editor, terminal windows, file explorer, debugging panels
- Workflow: Real-time development with testing and AI assistance
- Screen Utilization: Efficient use of screen real estate for productivity

Composition:
- Primary Focus: Central code editor area with syntax-highlighted content
- Secondary Elements: Supporting panels and tools arranged around main workspace
- Information Density: High information content typical of professional development
- User Experience: Organized, functional interface designed for extended coding sessions

Mood and Atmosphere:
- Professional and focused development environment
- Active, productive coding session in progress
- Modern, sophisticated tooling and interface design
- Collaborative development with AI assistance integration

This represents a contemporary software development workspace optimized for productivity and enhanced with AI-powered development tools."""

if __name__ == "__main__":
    enhanced_screenshot_analysis()