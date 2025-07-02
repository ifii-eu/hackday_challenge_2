import time
import json
import fitz  # PyMuPDF
import sys
from pymupdf import Point
from statistics import mean
from math import sqrt
import re
from os import mkdir
import os.path
import hashlib

#RAGflow interface
from ragflow import RagflowAPI

# GEMINI img2txt
from img2txt import Gemini
from dotenv import load_dotenv

IMG_OUTPUT_PATH = "output_img/"
HYPHENATION_LUT_PATH = "hyphenation/hyphenation_lut.json"
EXISTING_RESPONSES_DIR = "output_ai/"

TWINPAGE_BREAK = 0.5
PAGEFRAC_TWOCOLUMN_BREAKPONT = 0.5
LEFTCOLUMN_END = 0.3
RIGHTCOLUMN_START = 0.49

PAGE_HEADING_REGEX = re.compile(r"^\s*([0-9][0-9]*)\s*[^\.]*$")
SECTION_HEADING_REGEX = re.compile(r"^\s*([0-9][0-9]*\.[0-9][0-9]*)\s*[^\.]*$")
BOX_TYPE_IGNORE = ["Footnote", "Page footer"]

LIST_ITEM_REGEX = re.compile(r"^[-\*•]\s(.*)$")

MODEL_NAME_IMG2TXT = "gemini-1.5-flash"

# setup Gemini img2txt
load_dotenv() #load GOOGLE_API_KEY
img_ai = Gemini(MODEL_NAME_IMG2TXT)
IMG2TXT_PROMPT = "Nenne eine Überschrift für diese Grafik und bis zu drei der wichtigsten Fragen die die Grafik beantwortet sowie die entsprechenden Antworten. Fasse dich kurz und prägnant. Nutze das folgende Format:\n[GRAFIK]Titel: <Titel>\nFrage: <Frage>\n Antwort: <Antwort>\n[/GRAFIK]"
TABLE2TXT_PROMPT = "konvertiere diese Tabelle in JSON-Format. Wähle ob A: ein Eintrag pro Zeile und ein Attribut pro Spalte oder B: ein Eintrag pro Spalte und ein Attribut pro Zeile der Tabellenaufteilung entspricht. Gib nur den JSON-Code aus in folgendem Format:\n{\"title\":\"<table title>\",\"entries\":[{\"title\":\"<entry title>\",\"<attribute title>\":\"<attribute value>\",...}]}"

with open(HYPHENATION_LUT_PATH,"r") as file:
    hyphenation_lut = json.load(file)

def hash_ai_request_img(filepath,prompt,model):
    h = hashlib.sha256()
    with open(filepath,"rb") as file:
        img_content = file.read()
    h.update(len(img_content).to_bytes(4, 'big'))
    h.update(img_content)
    h.update(len(prompt).to_bytes(4, 'big'))
    h.update(prompt.encode('utf-8'))
    h.update(len(model).to_bytes(4, 'big'))
    h.update(model.encode('utf-8'))
    return h.hexdigest()    

def hash_ai_request(prompt,model):
    h = hashlib.sha256()
    h.update(len(prompt).to_bytes(4, 'big'))
    h.update(prompt.encode('utf-8'))
    h.update(len(model).to_bytes(4, 'big'))
    h.update(model.encode('utf-8'))
    return h.hexdigest()    

def get_ai_response(file,prompt):
    hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def generate_section_texts(sections,document_title="5G-Strategie des Landes Brandenburg"):
    toRet = []
    for section,items in sections.items():
        print(f"===\n{section} - {items}")
        sectiontext = "\n".join([format_markdown(it["text"],it["type"]) for it in items])
        heading = f"# Kapitel \"{section}\" aus dem Dokument \"{document_title}\" (Seiten {items[0]["pagenumber"]} bis {items[-1]["pagenumber"]})"
        toRet.append({"section":section,"heading":heading,"text":sectiontext})
    return toRet
    
def generate_chapter_summary(text,section,document_title="5G-Strategie des Landes Brandenburg"):
    CHAPTER_CONTEXT_PROMPT = f"Fasse Abschnitt {section} des Dokuments \"{document_title}\" zusammen. Nenne enthaltene Schlüsselinformationen und Fragen, die der Abschnitt beantwortet. Hier ist der Abschnitt:\n {text}"
    result = text_response(CHAPTER_CONTEXT_PROMPT)
    return result

def text_response(prompt):
    req_hash = hash_ai_request(prompt,MODEL_NAME_IMG2TXT)
    response_file_path = f"{EXISTING_RESPONSES_DIR}{req_hash}.resp"
    print(f"AI response requested with hash {req_hash}")
    if os.path.isfile(response_file_path):
        with open(response_file_path,"r") as file:
            response = file.read()
            print(f"using cached response for text prompt from {response_file_path}:\n\t{response}")
    else:
        if not os.path.exists(EXISTING_RESPONSES_DIR):
            mkdir(EXISTING_RESPONSES_DIR)
        response = img_ai.generate_response(input_text=prompt)
        with open(response_file_path,"w") as file:
            file.write(response)
            print(f"new response for text prompt stored in {response_file_path}")
    return response
    

def img_response(input, img):
    req_hash = hash_ai_request_img(img,input,MODEL_NAME_IMG2TXT)
    response_file_path = f"{EXISTING_RESPONSES_DIR}{req_hash}.resp"
    print(f"AI response requested with hash {req_hash}")
    if os.path.isfile(response_file_path):
        with open(response_file_path,"r") as file:
            response = file.read()
            print(f"using cached response for img {img} from {response_file_path}:\n\t{response}")
    else:
        if not os.path.exists(EXISTING_RESPONSES_DIR):
            mkdir(EXISTING_RESPONSES_DIR)
        response = img_ai.generate_response_img(input_text=input, input_img=img)
        with open(response_file_path,"w") as file:
            file.write(response)
            print(f"new response for img {img} stored in {response_file_path}")
    return response

def strip_list_item(item):
    match = LIST_ITEM_REGEX.match(item)
    if match and len(match.groups()) > 0:
        return match.groups()[0]
    else:
        return item

def format_markdown(text,item_type,precursor=None):
    if not text:
        return ""
    match(item_type):
        case "Text":
            precursorprefix = "\n" if precursor != "Text" else ""
            return f"{precursorprefix}\n{text}"
        case "Page heading":
            return f"\n\n# {text}\n\n"
        case "Sub heading":
            return f"\n\n## {text}\n\n"
        case "Subsub heading":
            return f"\n\n### {text}\n\n"
        case "List item":
            return f"\n* {strip_list_item(text)}"
        case "Table":
            return f"\n\n===START_TABLE===\n\n{text}\n\n===END_TABLE===\n\n"
        case "Picture":
            #return f"\n\n[Image Placeholder]\n\n"
            return f"\n\n===START_IMAGE===\n\n{text}\n\n===END_IMAGE===\n\n"
        case "PictureComp":
            #return f"\n\n[Image Placeholder]\n\n"
            return f"\n\n## {text.split("=!=!=")[0]}\n\n{f"![image](../../{text.split("=!=!=")[0]})"}\n\n{text.split("=!=!=")[1]}\n\n"
        case _:
            return text

def replace_multi(text,replachyphenation_lutements):
    toRet = text
    keys_to_replace=[key for key in hyphenation_lut.keys() if key in str(text)]
    if len(keys_to_replace) > 0:
        print(f"hyphenations to replace: {keys_to_replace}")
    for key in keys_to_replace:
        toRet = toRet.replace(key,hyphenation_lut[key])
    return toRet

def print_md(text,item_type,file):
    with open(file,"a",encoding="utf-8") as file:
        file.write(format_markdown(replace_multi(text,hyphenation_lut),item_type))

def analyse_pagewidth(doc):
    widths = [get_pagewidth(page) for page in doc]
    mean_width = mean(widths)
    deviation = mean([sqrt((mean_width-width)**2) for width in widths])
    return (mean_width,deviation)

def get_pagewidth(page,page_lr=None):
    if page_lr != None:
        pb = get_pagebox(page,page_lr)
        return pb["right"]-pb["left"]
    return page.mediabox_size[0]

def get_pageheight(page):
    return page.mediabox_size[1]

def get_bounding_box(box):
    return [box['left'],box['top'],float(box['left'])+float(box["width"]),float(box['top'])+float(box["height"])]

def get_lr_bounding_box(bbox):
    return{"left":bbox[0],"top":bbox[1],"right":bbox[2],"bot":bbox[3]}

def analyse_pageborders(boxes,page):
    pagewidth = get_pagewidth(page)
    if any([box for box in boxes if box["type"]=="Text"]):
        borders = (mean([entry["left"] for entry in boxes if entry["type"]=="Text"]),pagewidth-mean([float(entry["left"])+entry["width"] for entry in boxes if entry["type"]=="Text"]))
    else:
        borders = (0,0)
    return borders

def is_pageheading(box):
    return box["type"]=="Section header" and PAGE_HEADING_REGEX.match(box["text"])
def is_sectionheading(box):
    return box["type"]=="Section header" and SECTION_HEADING_REGEX.match(box["text"])

def get_page_headings(pageboxes):
    return [box for box in pageboxes if is_pageheading(box)]

def get_section_offsets(pageboxes):
    page_headings = get_page_headings(pageboxes)
    page_headings.sort(key= lambda b: float(b["top"]))
    sections = []
    last_offset = 0
    for page_heading in page_headings:
        sections.append((last_offset,float(page_heading["top"])))
        last_offset = float(page_heading["top"])
    return sections

def get_left_page_offset(page,page_lr):
    return 0 if page_lr=="left" else get_pagewidth(page,"left")

def get_box_pagehalf(page,page_lr,box):
    left_page_offset = get_left_page_offset(page,page_lr)
    if float(box["left"])+float(box["width"]) < left_page_offset + get_pagewidth(page,page_lr)*PAGEFRAC_TWOCOLUMN_BREAKPONT:
        return 1
    elif float(box["left"]) > left_page_offset + get_pagewidth(page,page_lr)*(1-PAGEFRAC_TWOCOLUMN_BREAKPONT):
        return 2
    else:
        return 0

def get_section_level(sections,box):
    for i,section in enumerate(sections):
        if float(box['top']) < section[1]:
            return i
    return 999
        
def get_boxtype_level(boxtype):
    order = ["Section header"]
    try:
        return order.index(boxtype)
    except ValueError:
        return 999

def get_pageheading_level(box):
    return 0 if is_pageheading(box) else 1

def get_heading_level(heading_text):
    if PAGE_HEADING_REGEX.match(heading_text):
        return 0
    if SECTION_HEADING_REGEX.match(heading_text):
        return 1
    return 2
def get_pagebox(page,page_lr):
    pagewidth = get_pagewidth(page)
    pageheight = get_pageheight(page)
    if page_lr == "left":
        return {"left":0,"top":0,"right":pagewidth*TWINPAGE_BREAK,"bot":pageheight}
    else:
        return {"left":pagewidth*TWINPAGE_BREAK,"top":0,"right":pagewidth,"bot":pageheight} 

def box_in_rect(box,pagebox):
    b = get_lr_bounding_box(get_bounding_box(box))
    if  b["left"] < pagebox["left"]:
        return False
    if  b["right"] > pagebox["right"]:
        return False
    if  b["top"] < pagebox["top"]:
        return False
    if  b["bot"] > pagebox["bot"]:
        return False
    return True

def is_pagespan_text(page,page_lr,box):
    # to rule out misclassified footnotes
    left_page_offset = get_left_page_offset(page,page_lr)
    if box["type"]!="Text":
        return False
    else:
        if box["left"] < left_page_offset + get_pagewidth(page,page_lr)*PAGEFRAC_TWOCOLUMN_BREAKPONT and box["left"]+box["width"] > left_page_offset + get_pagewidth(page,page_lr)*(1-PAGEFRAC_TWOCOLUMN_BREAKPONT):
            return True
        else:
            return False

def get_printed_pagenumber(pagenumber):
    return pagenumber-2 if pagenumber > 3 else 0

def save_img_box(box,page):
    if not os.path.exists(IMG_OUTPUT_PATH):
        mkdir(IMG_OUTPUT_PATH)
    clip_area = list(get_lr_bounding_box(get_bounding_box(box)).values())
    path_suffix = "_".join([str(int(x)) for  x in clip_area])
    pix = page.get_pixmap(clip=clip_area)
    img_path = f"{IMG_OUTPUT_PATH}img_{page.number}_{path_suffix}.png"
    pix.save(img_path)
    return img_path

def pagebox_sort_key(page,page_lr,sections,box):
    return (get_pageheading_level(box),get_box_pagehalf(page,page_lr,box),get_section_level(sections,box))

def overlay_boxes_on_pdf(pdf_path, json_path, pdf_output_path,md_output_dir):
    # prepare Ragflow dataset
    rapi = RagflowAPI()
    cd_resp = rapi.createDataset("output_"+output_suffix)
    dataset_id = cd_resp["data"]["id"]
    print(f"created dataset {dataset_id}.")
    doc_resp = rapi.addDocument("documents/strategie.pdf",dataset_id)
    doc_id = doc_resp["data"][0]["id"]
    print(f"created document {doc_id}.")
    
    # Load bounding boxes
    with open(json_path, 'r',encoding="utf-8") as f:
        boxes = json.load(f)

    # Open PDF
    doc = fitz.open(pdf_path)
    print(f"document read with {len(doc)} pages")
    # Overlay boxes

    pagewidth,mean_width_dev = analyse_pagewidth(doc)

    section=0
    subsection="<None>"

    sections_dict = dict()
    
    for pagenumber,page in enumerate(doc):
        for page_lr in ["left","right"]:
            pageboxes = [box for box in boxes if float(box["page_number"])-1==pagenumber and box_in_rect(box,get_pagebox(page,page_lr)) and box["type"] not in BOX_TYPE_IGNORE and not is_pagespan_text(page,page_lr,box)]
            imgboxes = [box for box in boxes if float(box["page_number"])-1==pagenumber and box_in_rect(box,get_pagebox(page,page_lr)) and box["type"] in ["Picture","Table"]]
            sections = get_section_offsets(pageboxes)
            pageboxes.sort(key=lambda box : pagebox_sort_key(page,page_lr,sections,box))
            for imgbox in imgboxes:
                img_path = save_img_box(imgbox,page)
                ai_response = img_response(input=IMG2TXT_PROMPT if imgbox["type"] == "Picture" else TABLE2TXT_PROMPT, img=img_path)
                print_md(f"{img_path}=!=!={ai_response}","PictureComp",f"{md_output_dir}/strategie_img_comp.md")
                print_md(ai_response,imgbox["type"],f"{md_output_dir}/strategie_section_{section}.md")
                chunk_resp = rapi.createChunk(ai_response,doc_id,dataset_id)
                #print(f"created chunk {chunk_resp["data"]["chunk"]["id"]}")
            print(f"page {pagenumber}({page_lr}) with {len(pageboxes)} boxes")
            for boxnumber,entry in enumerate(pageboxes):
                bbox = get_bounding_box(entry)  # [x0, y0, x1, y1]
                color = (0,0,0)
                # extract pagewidth
                # get left border
                pagewidth = get_pagewidth(page,page_lr)
                #borders = analyse_pageborders(pageboxes,page)

                column_type="" if entry["type"] != "Text" else ("onecolumn" if entry["width"] > pagewidth*PAGEFRAC_TWOCOLUMN_BREAKPONT else "twocolumn")

                boxtype = entry["type"]
                entry_text = entry["text"]

                if boxtype == "Text" and entry_text.isupper():
                    boxtype = "Section header"

                if boxtype in ["Section header"]:
                    print(f"analyzing heading {entry_text}:")

                    page_heading_match = PAGE_HEADING_REGEX.match(entry_text)
                    section_heading_match = SECTION_HEADING_REGEX.match(entry_text)

                    if page_heading_match:
                        print("...Page Heading")
                        boxtype = "Page heading"
                        #section = page_heading_match.groups()[0]
                        section = entry_text
                        subsection = "<None>"
                        print(f"setting section: {section}")
                        print(f"setting subsection: {subsection}")
                    elif section_heading_match:
                        print("...Section Heading")
                        boxtype = "Sub heading"
                        #subsection = section_heading_match.groups()[0]
                        subsection = entry_text
                        print(f"setting subsection: {subsection}")
                    else:
                        boxtype = "Subsub heading"
                        
                match entry["type"]:
                    case "Picture":
                        color = (1,0,0)
                    case "Text":
                        color = (0,0,1)
                    case "Section header":
                        color = (0,1,0)
                    case "List item":
                        color = (0,0.5,0.5)
                    case "Page footer":
                        color = (0,1,0)
                    case "Footnote":
                        color = (0,0.6,0)
                    case "Table":
                        color = (0.3,0.7,0.4)

                if pagenumber < 0 or pagenumber >= len(doc):
                    print(f"Invalid page number: {pagenumber}")
                    continue

                printed_pagenumber = get_printed_pagenumber(pagenumber*2+(1 if page_lr=="right" else 0))
                
                rect = fitz.Rect(bbox)
                page.draw_rect(rect, color=color, width=1)  # red box
                rc = page.insert_text(Point(bbox[0],bbox[1]-3),  # bottom-left of 1st char
                            f'page {printed_pagenumber} box {boxnumber} - {boxtype} - {column_type} - S: {section} - SS: {subsection} - {pagebox_sort_key(page,page_lr,sections,entry)}',# the text (honors '\n')
                            fontname = "helv",  # the default font
                            fontsize = 8,  # the default font size
                            rotate = 0,  # also available: 90, 180, 270
                            color=color
                            )
                chunk_text = replace_multi(entry_text,hyphenation_lut)
                if section not in sections_dict.keys():
                    sections_dict[str(section)] = []
                sections_dict[str(section)].append({"type":boxtype, "text":chunk_text, "pagenumber":printed_pagenumber, "subsection":subsection})
                print_md(chunk_text,boxtype,f"{md_output_dir}/strategie_section_{section}.md")
                rapi.createChunk(chunk_text,doc_id,dataset_id)
    # Save the output PDF
    for section in generate_section_texts(sections_dict):
        chunk_text = f"{section["heading"]}\n\n{str(generate_chapter_summary(section["text"],section["section"]))}"
        print(chunk_text)
        rapi.createChunk(chunk_text,doc_id,dataset_id)
        
    doc.save(pdf_output_path)
    print(f"Saved annotated PDF to: {pdf_output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python overlay_boxes.py input.pdf boxes.json output.pdf")
        sys.exit(1)
    pdf_path = sys.argv[1]
    json_path = sys.argv[2]
    output_suffix = str(time.time()).split(".")[0]
    pdf_output_path = f"output_pdf/output_{output_suffix}_{sys.argv[1].split("/")[-1]}"
    md_output_dir = f"output_md/output_{output_suffix}/"
    mkdir(md_output_dir)
    
    overlay_boxes_on_pdf(pdf_path, json_path, pdf_output_path,md_output_dir)
