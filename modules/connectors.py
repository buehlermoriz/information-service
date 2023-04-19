import openai



OPEN_AI_KEY = "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"

def request_open_ai(text: str, model: str, temp: float, max_tokens: int):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model=model, prompt=text, temperature=temp, max_tokens=max_tokens)

    return response["choices"][0]["text"]