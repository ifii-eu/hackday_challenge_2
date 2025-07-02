from img2txt import Gemini
from dotenv import load_dotenv


MODEL_NAME_IMG2TXT = "gemini-1.5-flash"
#IMG2TXT_PROMPT = "Fasse das im Folgenden beschriebene Projekt aus der 5G-Strategie des Landes Brandenburg in Zwei Sätzen zusammen. Erhalte die Informationen zu Zielgruppe und Fokus sowie eventuellen Kontaktdaten. Hier ist die Projektbeschreibung:\n"
IMG2TXT_PROMPT = "Fasse das folgende 5G-Projekt aus der 5G-Strategie des Landes Brandenburg in einem Satz zusammen. Gib nur den einen Satz an. Konzentriere dich auf den Projektinhalt und ignoriere administrative Informationen. Hier die Projektbeschreibung:\n"
load_dotenv() #load GOOGLE_API_KEY

img_ai = Gemini(MODEL_NAME_IMG2TXT)

with open("faq/assets/Projekte.md","r",encoding="utf-8") as file:
    text = file.read()
    
project_texts = text.split("=== CUT HERE ===")
print(f"{len(project_texts)} found")

with open("faq/output/project_out_7.md","a",encoding="utf-8") as file:
    for project_text in project_texts:
        pt = project_text.split("\n\n")
        info = pt[0]
        txt = pt[1]
        file.write("\n")
        file.write(f"{info}")
        file.write("\n")
        resp = img_ai.generate_response(input_text=f"{IMG2TXT_PROMPT}{txt}")
        print(f"{resp}")
        file.write(resp)
