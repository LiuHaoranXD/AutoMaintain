import google.generativeai as genai
genai.configure(api_key="你的GEMINI_API_KEY")
print(genai.list_models())
