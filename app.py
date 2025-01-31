# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 23:51:27 2025

@author: hamza
"""
import dash
from dash import dcc, html  
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
import pandas as pd


# Initialize Dash app
app = dash.Dash(__name__)

# Define neighboring countries
countries = ['AT', 'BE', 'CH', 'CZ', 'DK', 'FR', 'NL', 'NO', 'PL', 'SE']
years = list(range(2020, 2031))

# Generate random energy flow data (in MW) for each year
np.random.seed(42)
data = {
    year: {
        'imports': {country: np.random.randint(500, 5000) for country in countries},
        'exports': {country: np.random.randint(500, 5000) for country in countries}
    }
    for year in years
}

# Layout of the app
app.layout = html.Div([
    html.H1("Germany's Cross-Border Energy Flows (2020-2030)"),
    html.Label("Select Year:"),
    dcc.Slider(
        id='year-slider',
        min=min(years),
        max=max(years),
        value=min(years),
        marks={year: str(year) for year in years},
        step=1
    ),
    dcc.Graph(id='chord-diagram')
])

# Callback to update the chord diagram
@app.callback(
    Output('chord-diagram', 'figure'),
    [Input('year-slider', 'value')]
)
def update_chord(year):
    flows = data[year]
    
    labels = ['Germany'] + countries
    
    # Constructing Source, Target, and Values for Sankey (since Plotly lacks native Chord Diagram support)
    source, target, value = [], [], []
    
    for idx, country in enumerate(countries, start=1):
        source.append(0)  # Germany as source
        target.append(idx)  # Neighboring country as target
        value.append(flows['exports'][country])
        
        source.append(idx)  # Neighboring country as source
        target.append(0)  # Germany as target
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)