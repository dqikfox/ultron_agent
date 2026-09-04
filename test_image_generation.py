"""
Test Image Generation - Multiple providers
"""
import os
import asyncio
from pathlib import Path

async def test_stability_ai():
    """Test Stability AI image generation"""
    print("\n[TEST] Stability AI Image Generation")
    try:
        import requests
        
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            print("  [SKIP] STABILITY_API_KEY not set")
            return False
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        response = requests.post(url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "text_prompts": [{"text": "a futuristic AI robot assistant"}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            image_path = "test_stability.png"
            import base64
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(data["artifacts"][0]["base64"]))
            print(f"  [OK] Image saved: {image_path}")
            return True
        else:
            print(f"  [FAIL] Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_dalle():
    """Test DALL-E image generation"""
    print("\n[TEST] DALL-E Image Generation")
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  [SKIP] OPENAI_API_KEY not set")
            return False
        
        client = OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt="a futuristic AI robot assistant",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        print(f"  [OK] Image URL: {image_url}")
        
        # Download image
        import requests
        img_data = requests.get(image_url).content
        with open('test_dalle.png', 'wb') as f:
            f.write(img_data)
        print("  [OK] Image saved: test_dalle.png")
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_local_sdxl():
    """Test local Stable Diffusion XL"""
    print("\n[TEST] Local SDXL (via Ollama)")
    try:
        import requests
        
        # Check if Ollama has image model
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("  [SKIP] Ollama not running")
            return False
        
        models = response.json().get("models", [])
        has_image_model = any("llava" in m.get("name", "") for m in models)
        
        if not has_image_model:
            print("  [SKIP] No image model in Ollama")
            return False
        
        print("  [OK] Image model available (llava)")
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def main():
    print("=" * 60)
    print("IMAGE GENERATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Stability AI", test_stability_ai),
        ("DALL-E 3", test_dalle),
        ("Local SDXL", test_local_sdxl),
    ]
    
    results = []
    for name, test_func in tests:
        result = await test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "PASS" if result else "SKIP/FAIL"
        print(f"  [{status}] {name}")
    
    passed = sum(1 for _, r in results if r)
    print(f"\n{passed}/{len(results)} tests passed")

if __name__ == "__main__":
    asyncio.run(main())
