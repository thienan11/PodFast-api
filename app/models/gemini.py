import os
from google import genai

class Model:
    def __init__(self):
        google_api_key = os.getenv('GOOGLE_API_KEY')
        GEMINI_MODEL = "gemini-2.0-flash"

        client = genai.Client(api_key=google_api_key)

        self.model = GEMINI_MODEL
        self.client = client


    def get_response(self, query: str) -> str:
        try:
            res = self.client.models.generate_content(model=self.model, contents=query)
            if not res:
                return ""

            return res.text
        except Exception as e:
            print(f"Model.get_response: {str(e)}")
            return ""


    def execute_prompt_from_audio(self, prompt: str, audio_file_path: str) -> str:
        try:
            file = self.client.files.upload(file=audio_file_path)
            res = self.client.models.generate_content(model=self.model, contents=[prompt, file])
            if not res:
                return ""
        
            return res.text
        except Exception as e:
            print(f"Model.execute_prompt_from_audio: {str(e)}")
            return ""
