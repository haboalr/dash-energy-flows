# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 23:51:27 2025

@author: Hamza
"""

import os
import pypsa
import dash
from dash import dcc, html  
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd


# ===============================
# Configuration
# ===============================
NETWORKS_FOLDER = "Networks"  # Folder where network .nc files are stored
YEARS = list(range(2020, 2031))  # Years from 2020 to 2030
COUNTRIES = ['NO', 'FR', 'CH', 'AT', 'PL', 'NL', 'CZ', 'DK', 'BE', 'SE']


# ===============================
# Function: Load PyPSA Networks
# ===============================
def load_networks():
    """
    Loads PyPSA network files from the NETWORKS_FOLDER.

    Returns:
        dict: Dictionary where keys are years (2020-2030) and values are PyPSA networks.
    """
    networks = {}

    for year in YEARS:
        file_path = os.path.join(NETWORKS_FOLDER, f'{year}.nc')
        if os.path.exists(file_path):  # Check if the file exists
            networks[year] = pypsa.Network(file_path)
        else:
            print(f"Warning: {file_path} not found!")  # Debugging info
    
    return networks


# ===============================
# Function: Extract Import/Export Data
# ===============================
def get_import_export_data(networks):
    """
    Extracts import/export energy data for all years from the PyPSA networks.

    Parameters:
        networks (dict): A dictionary where keys are years (2020-2030) and values are PyPSA networks.

    Returns:
        dict: Nested dictionary with imports and exports data for each year and country.
    """
    data = {}

    for year, n in networks.items():
        country_links = {}

        for country_code in COUNTRIES:
            country_bus_id = f"{country_code}_imports"
            link_id = f"{country_bus_id}_link"
            if link_id in n.links.index:
                country_links[country_code] = link_id

        year_data = {'imports': {}, 'exports': {}}

        for country_code, link_id in country_links.items():
            p0 = n.links_t.p0[link_id]
            p1 = n.links_t.p1[link_id]  # p1 = -p0 if efficiency is 1

            # Sum over time to get total energy in MWh and convert to TWh
            total_imports_TWh = p0.clip(lower=0).sum() / 1e6
            total_exports_TWh = p1.clip(lower=0).sum() / 1e6

            year_data['imports'][country_code] = total_imports_TWh
            year_data['exports'][country_code] = total_exports_TWh

        data[year] = year_data

    return data


# ===============================
# Load Networks & Extract Data
# ===============================
networks = load_networks()
data = get_import_export_data(networks)


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
        min=min(YEARS),
        max=max(YEARS),
        value=min(YEARS),
        marks={year: str(year) for year in YEARS},
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
    flows = data[year]
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
