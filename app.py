# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 23:51:27 2025

@author: Hamza
"""

import random
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
    countries = list(flows['imports'].keys())

    labels = countries + ['Germany']  # Make Germany the target (last label)

    # Define colors for each country
    country_colors = {
        'NO': 'red',
        'FR': 'green',
        'CH': 'blue',
        'AT': 'orange',
        'PL': 'purple',
        'NL': 'brown',
        'CZ': 'cyan',
        'DK': 'magenta',
        'BE': 'lime',
        'SE': 'pink'
    }

    # Constructing Source, Target, Values, and Colors for Sankey
    source, target, value, link_colors = [], [], [], []

    for idx, country in enumerate(countries):
        # Imports: Country → Germany (Reversing direction)
        source.append(idx)  # Source is the country
        target.append(len(countries))  # Target is Germany
        value.append(flows['imports'][country])

        # Assign country-specific color to the link
        link_colors.append(country_colors.get(country, 'grey'))  # Default to grey if country not found

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors  # Assigning colors to each link
        )
    ))

    fig.update_layout(title_text=f"Energy Imports to Germany in {year}", font_size=10)
    
    return fig

# ===============================
# Run Server
# ===============================
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
