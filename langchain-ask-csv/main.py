from dash import Dash, html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import os
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.io as pio
import base64
import io
import PIL.Image
import tempfile
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from pathlib import Path

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Chatbot with Purple Theme"

app.layout = html.Div(
    children=[
        html.Div(
            id="chat-window",
        ),
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "padding": "10px",
                "background": "#f0f0f0",
                "borderRadius": "10px",
                "maxWidth": "800px",
                "margin": "20px auto",
            },
            children=[
                dbc.Input(
                    id="user-input",
                    placeholder="Type your message...",
                    type="text",
                    style={"flex": "1", "marginRight": "10px", "fontSize": "14px"},
                ),
                dbc.Button("Send", id="send-button", color="#6200ea", n_clicks=0),
                dcc.Upload(
                    id="upload-csv",
                    children=dbc.Button(
                        "📂",
                        color="#6200ea",
                        style={
                            "marginTop": "1px",
                            "textAlign": "center",
                            "fontSize": "30px",
                            "height": "50px",
                        },
                    ),
                    multiple=False,
                ),
            ],
        ),
    ],
)

conversation_history = []

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

def bot_response(user_message):
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
    if user_message == "Hi":
        chat_session = model.start_chat()
        response = chat_session.send_message(user_message)
        return response.text

    elif user_message == "I have few doubts":
        csv_filepath = r'C:\From Destop\interactive_visualization\langchain-ask-csv\data.csv'
        pdf_filepath = r'C:\Users\shankaripriya s\Downloads\output.pdf'
        csv_to_pdf(csv_filepath, pdf_filepath)
        media = Path(r'C:\Users\shankaripriya s\Downloads')
        sample_pdf = genai.upload_file(media / 'output.pdf')
        response3 = model.generate_content(["Give me a summary of this pdf file.", sample_pdf])
        return response3.text
    else:
        return "I'm sorry, I don't understand that message."



def parse_csv(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        except UnicodeDecodeError:
            df = pd.read_csv(io.StringIO(decoded.decode('latin-1')))
        return df
    except Exception as e:
        return f"Error parsing file: {e}"
 
def generate_graph(df):
    if df.shape[1] < 2:
        return "Not enough data for a graph. Please upload a CSV with at least two columns."
    fig = px.line(df, x=df.columns[0], y=df.columns[1], title="Line Graph")
    return dcc.Graph(figure=fig)

    
@app.callback(
    [Output("chat-window", "children"), Output("user-input", "value")],
    [Input("send-button", "n_clicks"), Input("upload-csv", "contents")],
    [State("user-input", "value"), State("chat-window", "children")],
)
def update_chat(n_clicks, uploaded_file, user_message, chat_history):
    if chat_history is None:
        chat_history = []
    if n_clicks > 0 and user_message:
        chat_history.append(
            html.Div(
                [
                    html.Img(src="/assets/user-avatar.png", className="avatar"),
                    html.Div(user_message, className="message-text"),
                ],
                className="message-container user",
            )
        )
        bot_reply = bot_response(user_message)
        chat_history.append(
            html.Div(
                [
                    html.Img(src="/assets/bot-avatar.png", className="avatar"),
                    html.Div(bot_reply, className="message-text"),
                ],
                className="message-container bot",
            )
        )
    if uploaded_file:
        chat_history.append(
            html.Div(
                [
                    html.Img(src="/assets/user-avatar.png", className="avatar"),
                    html.Div("Uploaded a CSV file", className="message-text"),
                ],
                className="message-container user",
            )
        )
        chat_history.append(
            html.Div(
                [
                    html.Img(src="/assets/bot-avatar.png", className="avatar"),
                    html.Div("CSV file uploaded successfully!", className="message-text"),
                ],
                className="message-container bot",
            )
        )
        

        df = parse_csv(uploaded_file)
        if isinstance(df, str): 
            chat_history.append(
                html.Div(
                    [
                        html.Img(src="/assets/bot-avatar.png", className="avatar"),
                        html.Div(df, className="message-text"),
                    ],
                    className="message-container bot",
                )
            )
        else:
            graph = generate_graph(df)
            
            chat_history.append(
                html.Div(
                    [
                        html.Img(src="/assets/bot-avatar.png", className="avatar"),
                        html.Div(graph, className="message-text"),
                    ],
                    className="message-container bot",
                )
            )

    return chat_history, ""

if __name__ == "__main__":
    app.run_server(debug=True)
