import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import openai
import io
import base64

openai.api_key = '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'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.H1("Data Visualization and Insights Generator", className="text-center my-4"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Describe the type of visualization:"),
                        dcc.Input(
                            id="visualization-input",
                            type="text",
                            placeholder="e.g., Bar chart of sales over time",
                            className="form-control"
                        ),
                        html.Label("Upload your CSV file:"),
                        dcc.Upload(
                            id="csv-upload",
                            children=html.Div(["Drag and Drop or Click to Upload"]),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                            },
                            multiple=False,
                        ),
                        dbc.Button("Generate", id="generate-button", color="primary", className="my-3"),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.H4("Visualization Output:", className="text-center"),
                        dcc.Graph(id="visualization-output"),
                        html.H4("Insights Summary:", className="text-center"),
                        html.Div(id="insights-output", style={"whiteSpace": "pre-wrap"}),
                    ],
                    width=8,
                ),
            ]
        ),
    ],
    fluid=True,
)

def generate_insights(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"


@app.callback(
    [Output("visualization-output", "figure"), Output("insights-output", "children")],
    [Input("generate-button", "n_clicks")],
    [State("visualization-input", "value"), State("csv-upload", "contents"), State("csv-upload", "filename")],
)
def generate_visualization_and_insights(n_clicks, viz_input, csv_contents, csv_filename):
    if not n_clicks or not csv_contents or not viz_input:
        return dash.no_update, dash.no_update

    content_type, content_string = csv_contents.split(",")
    decoded = io.StringIO(io.BytesIO(base64.b64decode(content_string)).read().decode("utf-8"))
    df = pd.read_csv(decoded)

    prompt = f"""
    Given the following text: "{viz_input}", and the dataset: {df.head().to_dict()},
    interpret the type of visualization and provide insights or summary based on the data.
    """
    insights = generate_insights(prompt)

    if "bar" in viz_input.lower():
        figure = px.bar(df, x=df.columns[0], y=df.columns[1], title="Bar Chart")
    elif "line" in viz_input.lower():
        figure = px.line(df, x=df.columns[0], y=df.columns[1], title="Line Graph")
    elif "scatter" in viz_input.lower():
        figure = px.scatter(df, x=df.columns[0], y=df.columns[1], title="Scatter Plot")
    else:
        figure = px.histogram(df, x=df.columns[0], title="Default Histogram")

    return figure, insights


if __name__ == "__main__":
    app.run_server(debug=True)
