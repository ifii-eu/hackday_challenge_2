from img2txt import GeminiImg

from dotenv import load_dotenv

load_dotenv()

TABLE2TXT_PROMPT = "konvertiere diese Tabelle in JSON-Format. Wähle ob A: ein Eintrag pro Zeile und ein Attribut pro Spalte oder B: ein Eintrag pro Spalte und ein Attribut pro Zeile der Tabellenaufteilung entspricht. Gib nur den JSON-Code aus in folgendem Format:\n{\"title\":\"<table title>\",\"entries\":[{\"title\":\"<entry title>\",\"<attribute title>\":\"<attribute value>\",...}]}"

model_name_img = "gemini-1.5-flash"
your_img_ai = GeminiImg(model_name_img)

def img_response(input, img):
    return your_img_ai.generate_response(input_text=input, input_img=img)

if __name__ == "__main__":
    #prompt = "Nenne eine Überschrift für diese Grafik und bis zu drei der wichtigsten Fragen die die Grafik beantwortet sowie die entsprechenden Antworten. Fasse dich kurz und prägnant. Nutze das folgende Format:\n[GRAFIK]Titel: <Titel>\nFrage: <Frage>\n Antwort: <Antwort>\n[/GRAFIK]"
    prompt = TABLE2TXT_PROMPT
    img = "output_img/img_11_643_515_1140_639.png"
    print(img_response(input=prompt, img=img))