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
    Generates a luxurious wide-format Sankey diagram with vibrant scientific styling.
    """
    flows = data[str(year)]
    countries = list(flows['imports'].keys())
    labels = ['Germany'] + countries

    # Enhanced vibrant scientific color palette
    country_colors = {
        'NO': '#00A0B0',  # Bright teal
        'FR': '#1E88E5',  # Vibrant blue
        'CH': '#26A69A',  # Green-teal
        'AT': '#FF7043',  # Coral orange
        'PL': '#5C6BC0',  # Indigo blue
        'NL': '#FFA726',  # Warm orange
        'CZ': '#2E7D32',  # Forest green
        'DK': '#00ACC1',  # Cyan
        'BE': '#43A047',  # Vivid green
        'SE': '#039BE5'   # Light blue
    }

    # Generate vibrant node colors
    node_colors = ['#263238'] + [country_colors.get(country, '#546E7A') for country in countries]

    source, target, value, link_colors, hover_labels = [], [], [], [], []

    def create_gradient_color(base_color, direction='imports'):
        rgb = tuple(int(base_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        if direction == 'imports':
            return f'rgba{rgb + (0.85,)}'  # More opacity for better visibility
        return f'rgba{rgb + (0.6,)}'       # More opacity for exports too

    for idx, country in enumerate(countries, start=1):
        import_value = flows['imports'][country]
        export_value = flows['exports'][country]

        # Enhanced imports styling
        source.append(idx)
        target.append(0)
        value.append(import_value)
        base_color = country_colors.get(country, '#546E7A')
        link_colors.append(create_gradient_color(base_color, 'imports'))
        hover_labels.append(
            f"<b>{country} → Germany</b><br>" +
            f"Import: {import_value:.1f} TWh<br>" +
            f"<span style='font-size:0.9em; color: #666'>Click to highlight flow</span>"
        )

        # Enhanced exports styling
        source.append(0)
        target.append(idx)
        value.append(export_value)
        link_colors.append(create_gradient_color(base_color, 'exports'))
        hover_labels.append(
            f"<b>Germany → {country}</b><br>" +
            f"Export: {export_value:.1f} TWh<br>" +
            f"<span style='font-size:0.9em; color: #666'>Click to highlight flow</span>"
        )

    # Create the enhanced Sankey diagram
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=35,
            thickness=35,
            line=dict(color="#fff", width=1.5),
            label=labels,
            color=node_colors,
            customdata=labels,
            hovertemplate="<b>%{customdata}</b><br>" +
                         "Total Flow: %{value:.1f} TWh<br>" +
                         "<i>Click to highlight connections</i><extra></extra>",
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            customdata=hover_labels,
            hovertemplate="%{customdata}<extra></extra>"
        )
    ))

    # Enhanced layout styling
    fig.update_layout(
        title=dict(
            text=f"Germany's Energy Trade Balance {year}",
            font=dict(
                size=32,
                family="Arial",
                color='#1A237E'
            ),
            x=0.5,
            y=0.98
        ),
        font=dict(
            family="Arial",
            size=14,
            color='#37474F'
        ),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        width=1800,  # Even wider format
        height=900,  # Increased height
        margin=dict(t=120, l=60, r=60, b=60),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.05,
                y=1.15,
                buttons=[
                    dict(
                        label="Reset View",
                        method="relayout",
                        args=["xaxis.range", None]
                    )
                ]
            )
        ],
        annotations=[
            dict(
                text="TWh (Terawatt Hours)",
                showarrow=False,
                x=0.5,
                y=-0.1,
                xref="paper",
                yref="paper",
                font=dict(size=16, color='#37474F')
            )
        ]
    )

    # Add subtle pattern background
    for i in range(0, 101, 10):
        fig.add_shape(
            type="line",
            x0=0,
            y0=i/100,
            x1=1,
            y1=i/100,
            xref="paper",
            yref="paper",
            line=dict(color="#F5F5F5", width=1)
        )

    return fig

# ===============================
# Run Server
# ===============================
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
