#!/usr/bin/env python3
"""
Direct Stable Diffusion Tool Test
"""

from tools.stable_diffusion_tool import StableDiffusionTool

def main():
    tool = StableDiffusionTool()
    command = "generate image of a beautiful mountain landscape at sunset"
    result = tool.execute(command)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
