from google.generativeai.types import HarmCategory, HarmBlockThreshold

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def safe_generate(model, prompt):
    response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
    try:
        return response.text
    except ValueError:
        if response.candidates:
            print("Safety ratings:", response.candidates[0].safety_ratings)
        raise ValueError("⚠️ Gemini blocked the response. Try rephrasing your query.")