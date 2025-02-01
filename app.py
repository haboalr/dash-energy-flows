# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 23:51:27 2025

@author: Hamza
"""

import dash
from dash import dcc, html  
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import json

# ===============================
# Load Preprocessed Data
# ===============================
with open("data.json", "r") as f:
    data = json.load(f)

YEARS = list(data.keys())
COUNTRIES = list(data[str(YEARS[0])]['imports'].keys())

# ===============================
# Dash App Initialization
# ===============================
app = dash.Dash(__name__)

# ===============================
# Layout
# ===============================
app.layout = html.Div([
    html.H1("Germany's Cross-Border Energy Flows (2020-2030)"),
    
    html.Label("Select Year:"),
    dcc.Slider(
        id='year-slider',
        min=int(min(YEARS)),
        max=int(max(YEARS)),
        value=int(min(YEARS)),
        marks={int(year): str(year) for year in YEARS},
        step=1
    ),
    
    dcc.Graph(id='chord-diagram')
])

# ===============================
# Callback: Update Chord Diagram
# ===============================
@app.callback(
    Output('chord-diagram', 'figure'),
    [Input('year-slider', 'value')]
)
def update_chord(year):
    """
    Generates a Sankey diagram for energy imports/exports for the selected year.

    Parameters:
        year (int): Selected year from the slider.

    Returns:
        plotly.graph_objects.Figure: Sankey diagram visualization.
    """
    flows = data[str(year)]
    labels = ['Germany'] + list(flows['imports'].keys())

    # Constructing Source, Target, and Values for Sankey
    source, target, value = [], [], []

    for idx, country in enumerate(flows['imports'].keys(), start=1):
        # Exports from Germany -> Country
        source.append(0)  
        target.append(idx)
        value.append(flows['exports'][country])
        
        # Imports from Country -> Germany
        source.append(idx)  
        target.append(0)
        value.append(flows['imports'][country])

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    ))

    fig.update_layout(title_text=f"Energy Flows Between Germany and Neighbors in {year}", font_size=10)
    
    return fig

# ===============================
# Run Server
# ===============================
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
