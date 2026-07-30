from groq import AsyncGroq
from app.config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)

async def ask_groq(prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Актуальная модель Groq вместо выведенной из эксплуатации
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка ИИ-сервиса: {e}"