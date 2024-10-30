import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

async def analyze_code(contents: str) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Analyze the following code: {contents}",
        max_tokens=150
    )
    return response.choices[0].text.strip()
