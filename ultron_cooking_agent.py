"""
ULTRON Cooking AI Agent Console App
- Uses Microsoft Agent Framework (GitHub Model)
- Features: Recipe search, ingredient extraction
"""
import asyncio
from agentframework import Agent, Tool, AgentContext
import requests
from bs4 import BeautifulSoup

# --- Tool: Recipe Search ---
class RecipeSearchTool(Tool):
    name = "recipe_search"
    description = "Search for recipes online and return top results."

    async def execute(self, context: AgentContext, query: str) -> str:
        url = f"https://duckduckgo.com/html/?q={query}+recipe"
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for a in soup.select('.result__a')[:3]:
            results.append(f"- {a.get_text(strip=True)}: {a['href']}")
        return "\n".join(results) if results else "No recipes found."

# --- Tool: Ingredient Extraction ---
class IngredientExtractionTool(Tool):
    name = "extract_ingredients"
    description = "Extract ingredients from a recipe web page URL."

    async def execute(self, context: AgentContext, url: str) -> str:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            # Simple heuristic: look for <li> elements under 'ingredients' sections
            ingredients = []
            for section in soup.find_all(['section', 'div'], string=lambda s: s and 'ingredient' in s.lower()):
                for li in section.find_all('li'):
                    ingredients.append(li.get_text(strip=True))
            if not ingredients:
                # Fallback: all <li> elements
                ingredients = [li.get_text(strip=True) for li in soup.find_all('li')]
            return "\n".join(ingredients[:20]) if ingredients else "No ingredients found."
        except Exception as e:
            return f"Error extracting ingredients: {e}"

# --- Main Agent ---
class UltronCookingAgent(Agent):
    def __init__(self, model="gpt-3.5-turbo"):
        super().__init__(model=model)
        self.add_tool(RecipeSearchTool())
        self.add_tool(IngredientExtractionTool())

    async def interact(self):
        print("Welcome to the ULTRON Cooking AI Agent! Type 'exit' to quit.")
        while True:
            user = input("You: ").strip()
            if user.lower() == "exit":
                print("Goodbye!")
                break
            response = await self.run(user)
            print(f"Agent: {response}")

if __name__ == "__main__":
    agent = UltronCookingAgent()
    asyncio.run(agent.interact())
