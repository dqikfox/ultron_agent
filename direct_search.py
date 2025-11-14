import requests
import sys

print("=== DIRECT AI NEWS SEARCH ===")
print()

try:
    # Direct search without tool wrapper
    url = "https://html.duckduckgo.com/html/"
    params = {"q": "AI news 2025 artificial intelligence breakthrough"}
    
    print("Searching DuckDuckGo for AI news...")
    response = requests.get(url, params=params, timeout=10)
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)} characters")
    
    if response.status_code == 200:
        content = response.text
        
        # Extract some visible content
        import re
        
        # Look for result titles
        titles = re.findall(r'<a[^>]*class="result__a"[^>]*>([^<]+)</a>', content)
        if titles:
            print("\nFOUND AI NEWS TITLES:")
            for i, title in enumerate(titles[:5], 1):
                print(f"{i}. {title.strip()}")
        
        # Look for snippets
        snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>([^<]+)</a>', content)
        if snippets:
            print("\nNEWS SNIPPETS:")
            for i, snippet in enumerate(snippets[:3], 1):
                print(f"{i}. {snippet.strip()[:100]}...")
        
        # Check for AI-related keywords
        ai_keywords = ["artificial intelligence", "AI", "machine learning", "neural", "GPT", "ChatGPT", "OpenAI"]
        found_keywords = [kw for kw in ai_keywords if kw.lower() in content.lower()]
        
        if found_keywords:
            print(f"\nAI KEYWORDS FOUND: {', '.join(found_keywords)}")
        
        print(f"\nSUCCESS: Retrieved {len(content)} characters of AI news content")
        
    else:
        print(f"Search failed with status code: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== SEARCH COMPLETE ===")