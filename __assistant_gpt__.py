import openai

class Assistant:
    def __init__(self,message):
        client = openai.OpenAI(
            api_key="",  # This is the default and can be omitted
        )
        self.chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="gpt-4o",
        )
    def __result__(self):
        return self.chat_completion
