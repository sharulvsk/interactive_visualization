import os
import google.generativeai as genai
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import csv


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("HI")

def csv_to_pdf(csv_filepath, pdf_filepath):
    """Converts a CSV file to a PDF file."""
    try:
        with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  
            data = list(reader) 

        c = canvas.Canvas(pdf_filepath, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica", 12)
        x = 0.5 * inch
        y = height - 0.5 * inch

        for col in header:
            c.drawString(x, y, col)
            x += 1.5 * inch 
        c.showPage()  
        x = 0.5 * inch
        y = height - 0.5 * inch

        for row in data:
            x = 0.5 * inch
            for col in row:
                c.drawString(x, y, col)
                x += 1.5 * inch
            y -= 0.25 * inch 
            if y < 1 * inch:
                c.showPage()
                y = height - 0.5 * inch


        c.save()
        print(f"CSV converted to PDF successfully: {pdf_filepath}")

    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

csv_filepath = r'C:\From Destop\interactive_visualization\langchain-ask-csv\data.csv'  
pdf_filepath = r'C:\Users\shankaripriya s\Downloads\output.pdf'       
csv_to_pdf(csv_filepath, pdf_filepath)

media = Path(r'C:\Users\shankaripriya s\Downloads')
sample_pdf = genai.upload_file(media / 'output.pdf')
response = model.generate_content(["Give me a summary of this pdf file.", sample_pdf])
print(response.text)

print(response.text)
