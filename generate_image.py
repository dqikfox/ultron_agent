#!/usr/bin/env python3
"""
Direct image generation script using Stable Diffusion Tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.stable_diffusion_tool import StableDiffusionTool


def main():
    print("🖼️  Creating image using Stable Diffusion Tool...")

    # Create tool instance
    tool = StableDiffusionTool()

    # Generate image
    command = "generate image of a beautiful mountain landscape at sunset"
    result = tool.execute(command)

    print(f"📄 Result: {result}")

    if "successfully" in result.lower():
        print("✅ Image generation completed!")
    else:
        print("❌ Image generation failed.")


if __name__ == "__main__":
    main()
