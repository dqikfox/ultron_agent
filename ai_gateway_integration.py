#!/usr/bin/env python3
"""
AI Gateway Integration for ULTRON Agent
This module provides integration with Vercel's AI Gateway for unified AI provider access.
"""

import os
import asyncio
import subprocess
import json
from typing import Optional, Dict, Any
from pathlib import Path

class AIGatewayIntegration:
    """Integration class for Vercel's AI Gateway"""

    def __init__(self, gateway_api_key: Optional[str] = None):
        self.gateway_api_key = gateway_api_key or os.getenv('AI_GATEWAY_API_KEY')
        self.node_script_path = Path(__file__).parent / "ai_gateway_call.js"

    async def generate_text(self, prompt: str, model: str = "openai/gpt-4.1") -> Optional[str]:
        """
        Generate text using AI Gateway

        Args:
            prompt: The text prompt to send
            model: The model to use (default: openai/gpt-4.1)

        Returns:
            Generated text or None if failed
        """
        if not self.gateway_api_key:
            print("❌ AI_GATEWAY_API_KEY not set")
            return None

        # Create temporary Node.js script for this call
        script_content = f"""
import {{ streamText }} from 'ai';
import 'dotenv/config';

process.env.AI_GATEWAY_API_KEY = '{self.gateway_api_key}';

async function generate() {{
  try {{
    const result = streamText({{
      model: '{model}',
      prompt: {json.dumps(prompt)},
    }});

    let fullText = '';
    for await (const textPart of result.textStream) {{
      fullText += textPart;
      process.stdout.write(textPart);
    }}

    console.log('\\n---END---');
    console.log('Token usage:', JSON.stringify(await result.usage));
  }} catch (error) {{
    console.error('Error:', error.message);
    process.exit(1);
  }}
}}

generate();
"""

        try:
            # Write script to temporary file
            with open(self.node_script_path, 'w') as f:
                f.write(script_content)

            # Run the Node.js script
            result = await asyncio.create_subprocess_exec(
                'npx', 'tsx', str(self.node_script_path),
                cwd=Path(__file__).parent,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                output = stdout.decode().strip()
                # Parse the output (text before ---END---)
                if '---END---' in output:
                    text_part = output.split('---END---')[0]
                    return text_part.strip()
                return output
            else:
                print(f"❌ AI Gateway call failed: {stderr.decode()}")
                return None

        except Exception as e:
            print(f"❌ Error calling AI Gateway: {e}")
            return None
        finally:
            # Clean up temporary script
            if self.node_script_path.exists():
                self.node_script_path.unlink()

    async def check_gateway_status(self) -> bool:
        """Check if AI Gateway is accessible"""
        test_result = await self.generate_text("Hello", "openai/gpt-3.5-turbo")
        return test_result is not None


# Example usage and integration with ULTRON Agent
async def demo_integration():
    """Demo function showing how to integrate AI Gateway with ULTRON Agent"""

    # Initialize the integration
    ai_gateway = AIGatewayIntegration()

    # Check if gateway is working
    if await ai_gateway.check_gateway_status():
        print("✅ AI Gateway is working!")

        # Generate some text
        result = await ai_gateway.generate_text(
            "Explain the benefits of AI Gateway for unified AI provider access."
        )

        if result:
            print("🤖 AI Gateway Response:")
            print(result)
        else:
            print("❌ Failed to generate text")
    else:
        print("❌ AI Gateway is not accessible")
        print("💡 Make sure AI_GATEWAY_API_KEY is set and you have a credit card on file with Vercel")


if __name__ == "__main__":
    asyncio.run(demo_integration())
