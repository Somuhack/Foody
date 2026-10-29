import os
from google import genai
from google.genai import types
from pydantic import BaseModel

# Initialize the Gemini client
# It will automatically pick up the GEMINI_API_KEY environment variable
client = genai.Client()

class SearchIntent(BaseModel):
    search_terms: list[str]

def expand_search_query(query: str) -> list[str]:
    try:
        # gemini-2.5-flash is fast, accurate, and has a generous free tier
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "you help search an ecommerce product catalog. "
                    "Convert the user's search into short list of "
                    "useful product search terms and synonyms. "
                    "Preserve the user's intent. "
                    "Return 3 to 6 concise terms or phrases. "
                    "include usefull English Equivalents for non-English "
                    "queries when appropriate. "
                    "Do not invent product facts or filters."
                ),
                # Enforce structured output using your Pydantic schema
                response_mime_type="application/json",
                response_schema=SearchIntent,
            ),
        )
        
        # Parse the JSON response text back into the Pydantic model
        result = SearchIntent.model_validate_json(response.text)
        
        terms = [
            term.strip()
            for term in result.search_terms
            if term.strip()
        ]
        return list(dict.fromkeys([query, *terms]))[:7]

    except Exception as e:
        # Fallback to the original query if the API call fails or times out
        print(f"Gemini expansion failed: {e}")
        return [query]
