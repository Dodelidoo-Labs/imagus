import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image, Table, TableStyle, PageBegin)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

doc = SimpleDocTemplate("comic.pdf", pagesize=letter)
story = []
table_data = []
styles = getSampleStyleSheet()
comicTextStyle = styles["BodyText"].clone('comicTextStyle')
comicTextStyle.spaceAfter = 15
page_width, page_height = letter
gap = 15
img_width = (page_width - 3 * gap) / 2
img_height = (page_height - 6 * gap) / 4
page_num = 1
comic_title = input("Enter your Comic Title:")
dodelidoo_url = "https://dodelidoo.com"
imagus_url = "https://github.com/dodelidoo-labs/imagus"
copy_pre = "Generated with "
copy_imagus = "iMagus"
copy_after = " by "
copy_dodelidoo = "Dodelidoo Labs"
full_copy_text = copy_pre + copy_imagus + copy_after + copy_dodelidoo
link_height = 12

with open('logs.json', 'r') as f:
    data = json.load(f)

def on_first_page(canvas, doc):
    on_page(canvas, doc, is_first_page=True)

def on_later_pages(canvas, doc):
    global page_num
    page_num += 1
    on_page(canvas, doc, is_first_page=False)

def on_page(canvas, doc, is_first_page):

    canvas.saveState()
    
    if is_first_page:
        canvas.setFont("Helvetica", 20)
        canvas.drawCentredString(doc.width / 2.0 + doc.leftMargin, doc.height + 1 * inch, comic_title)

    canvas.setFont("Helvetica", 10)
    x_start = (doc.width - stringWidth(full_copy_text, "Helvetica", 10)) / 2.0 + doc.leftMargin
    y = 0.5 * inch
    x_imagus_start = x_start + stringWidth(copy_pre, "Helvetica", 10)
    x_imagus_end = x_imagus_start + stringWidth(copy_imagus, "Helvetica", 10)
    x_dodelidoo_start = x_imagus_end + stringWidth(copy_after, "Helvetica", 10)
    x_dodelidoo_end = x_dodelidoo_start + stringWidth(copy_dodelidoo, "Helvetica", 10)
    canvas.drawString(x_start, y, full_copy_text)
    canvas.setFillColorRGB(0, 0, 1)
    canvas.drawString(x_imagus_start, y, copy_imagus)
    canvas.drawString(x_dodelidoo_start, y, copy_dodelidoo)
    canvas.linkURL(imagus_url, (x_imagus_start, y, x_imagus_end, y + link_height), relative=1)
    canvas.linkURL(dodelidoo_url, (x_dodelidoo_start, y, x_dodelidoo_end, y + link_height), relative=1)
    canvas.setFillColorRGB(0, 0, 0)
    canvas.drawString(doc.width + doc.leftMargin, 0.5 * inch, f"Page {page_num}")

    canvas.restoreState()

def format_description(desc):
    parts = []
    if 'narration' in desc:
        for line in desc['narration']:
            parts.append(f"<i>{line}</i>")
    if 'dialogue' in desc:
        for d in desc['dialogue']:
            parts.append(f"<b>{d['character']}:</b> {d['text']}")
    if 'sfx' in desc:
        for s in desc['sfx']:
            parts.append(f"<font color='gray'>{s}</font>")
    return '<br/>'.join(parts)

for i in range(0, len(data), 4):
    row_images = []
    row_texts = []
    for j in range(4):
        if i + j < len(data):
            item = data[i + j]
            img = Image(f"imgs/{(i + j)}-image.png", img_width, img_height)
            para_text = format_description(item["description"])
            para = Paragraph(para_text, comicTextStyle)
            
            if j % 2 == 0 and j != 0:
                table_data.append(row_images)
                table_data.append(row_texts)
                row_images, row_texts = [], []
            row_images.append(img)
            row_texts.append(para)
    
    if row_images and row_texts:
        table_data.append(row_images)
        table_data.append(row_texts)

    if (i + 4) % 4 == 0 and i != 0:
        story.append(PageBegin())

col_widths = [img_width + gap, img_width + gap]

table = Table(table_data, colWidths=col_widths)
table.setStyle(TableStyle([
    ('PAD', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 15),
    ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ('LEFTPADDING', (0,0), (0,-1), 15),
    ('RIGHTPADDING', (-1,0), (-1,-1), 15),
]))

story.append(table)
doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
