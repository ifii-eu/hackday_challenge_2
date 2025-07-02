import os
import google.generativeai as genai

from PIL import Image


def sayhello():
    print("hello")

class Gemini:
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY")

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            print(f"Failed to initialize Gemini Model: {e}")

    def generate_response_img(self, input_text, input_img):
        """ Generates a response out of an image and a promt (optional) using the Gemini vision model"""
        try:
            img = Image.open(input_img)
            response = self.model.generate_content([input_text, img], stream=True)
            response.resolve()
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
    def generate_response(self, input_text):
        """ Generates a response out of an image and a promt (optional) using the Gemini vision model"""
        try:
            response = self.model.generate_content([input_text], stream=True)
            response.resolve()
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return None