#!/usr/bin/env python3
"""
ULTRON Agent OCR Test Script

This script demonstrates the OCR capabilities of the vision system.
Run this to verify OCR is working correctly on your screen.
"""

from vision import Vision
import time

def test_ocr():
    print("🔍 ULTRON Agent OCR Test")
    print("=" * 50)

    # Initialize vision system
    v = Vision()
    print(f"Tesseract OCR Available: {'✅ Yes' if v.tesseract_available else '❌ No'}")

    if not v.tesseract_available:
        print("❌ OCR not available. Please install Tesseract:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        return

    print("\n📸 Taking screenshot and performing OCR...")
    print("   (Make sure your screen has some readable text visible)")

    # Capture and analyze
    result = v.capture_and_ocr()

    print("\n📊 OCR Results:")
    print(f"   Screenshot saved: {result['screenshot_path']}")
    print(f"   Text detected: {'✅ Yes' if result['has_text'] else '❌ No'}")
    print(f"   Word count: {result['word_count']}")
    print(f"   Character count: {result['char_count']}")

    if result['has_text']:
        print("\n📝 Text Preview (first 300 characters):")
        preview = result['text'][:300].replace('\n', ' | ')
        print(f"   {preview}...")

        # Show some sample lines
        lines = [line.strip() for line in result['text'].split('\n') if line.strip()]
        if lines:
            print("\n📋 Sample detected lines:")
            for i, line in enumerate(lines[:3]):
                print(f"   {i+1}. {line[:60]}{'...' if len(line) > 60 else ''}")

        print("\n✅ SUCCESS: OCR is working correctly!")
        print("   Your vision system can read text from screenshots.")

    else:
        print("\n⚠️  No text detected. This could mean:")
        print("   - The screen is blank or contains only images")
        print("   - Text is too small or unclear")
        print("   - Try opening a document or webpage with text")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_ocr()
