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
    Generates a Sankey diagram for energy imports and exports for the selected year.

    Parameters:
        year (int): Selected year from the slider.

    Returns:
        plotly.graph_objects.Figure: Sankey diagram visualization.
    """
    flows = data[str(year)]
    countries = list(flows['imports'].keys())

    labels = ['Germany'] + countries  # Germany is now first in the list

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

    # Construct Source, Target, Values, Colors, and Hover Labels for Sankey
    source, target, value, link_colors, hover_labels = [], [], [], [], []

    for idx, country in enumerate(countries, start=1):  # Start at 1 since Germany is 0
        import_value = flows['imports'][country]  # Value in TWh
        export_value = flows['exports'][country]  # Value in TWh

        # Imports: Country → Germany
        source.append(idx)  # Source is the country
        target.append(0)  # Target is Germany
        value.append(import_value)  # Line width proportional to value
        link_colors.append(country_colors.get(country, 'grey'))  # Assign country color
        hover_labels.append(f"{country} → Germany: {import_value:.2f} TWh")

        # Exports: Germany → Country
        source.append(0)  # Source is Germany
        target.append(idx)  # Target is the country
        value.append(export_value)  # Line width proportional to value
        link_colors.append(country_colors.get(country, 'grey'))  # Assign same country color
        hover_labels.append(f"Germany → {country}: {export_value:.2f} TWh")

    # Create Sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=labels,
            color="black"  # Make node text black for visibility
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,  # Ensure the color matches the country
            customdata=hover_labels,
            hovertemplate='%{customdata}<extra></extra>'  # Shows values on hover
        )
    ))

    fig.update_layout(title_text=f"Germany's Energy Trade Balance in {year} (TWh)", font_size=10)
    
    return fig


# ===============================
# Run Server
# ===============================
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
