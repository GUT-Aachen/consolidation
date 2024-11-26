import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
import time


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.title = 'Consolidation'
app._favicon = ('assets/favicon.ico')

# Updated layout with sliders on top and layer properties below
app.layout = html.Div([
    # Main container
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'height': '100vh'}, children=[
        # Control container (sliders)
        html.Div(id='control-container', style={'width': '25%', 'padding': '2%', 'flexDirection': 'column'}, children=[
            html.H1('Consolidation', className='h1'),

            # Add the update button
            html.Button("Update Graphs", id='update-button', n_clicks=0, style={'width': '100%', 'height': '5vh', 'marginBottom': '1vh'}),

            # Sliders for each layer
            html.Div(className='slider-container', children=[
                # Sand-1 Slider
                html.Label(children=[
                    'Z', html.Sub('1'), ' (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of Sand-1.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='z-1', min=0, max=20, step=0.25, value=2,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Clay Slider
                html.Label(children=[
                    'Z', html.Sub('2'), ' (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of Clay.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='z-2', min=0, max=20, step=0.25, value=4,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Sand-2 Slider
                html.Label(children=[
                    'Z', html.Sub('3'), ' (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of Sand-2.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='z-3', min=0, max=20, step=0.25, value=2,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Water table slider
                html.Label(children=[
                    "Water Table", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Water table depth from the surface.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='water-table', min=0, max=4, step=0.25, value=0,
                    marks={i: f'{i}' for i in range(0, 5, 2)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),
                # time slider
                html.Label(children=[
                    "Time", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Time for consolidation.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='time-slider', min=0, max=100, step=1, value=0,
                    marks={0: '0', 100: '∞'},
                    tooltip=None,  updatemode='drag'
                ),

            ]),
        
        # Properties for each layer
        html.Div(className='layer-properties', children=[
                # foundation Properties
                html.H3('Load:', style={'textAlign': 'left'}, className='h3'),
                    html.Label(["Δσ", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Chnage of stress', className='tooltiptext')
                            ]),'(kPa)'], className='input-label'),
                dcc.Input(id='delta_sigma', type='number', value=100, step=1, className='input-field'),


                # Sand-1 Properties
                html.H3('Sand-1:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Sand-1', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_1', type='number', value=18, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Sand-1', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_1', type='number', value=19, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Sand-1', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_1', className='input-field')  
                ]),


                # Clay Properties
                html.H3('Clay:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Clay', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_2', type='number', value=19, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Caly', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_2', type='number', value=21, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Clay', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_2',className='input-field')  
                ]),
                html.Label([f'c', html.Sub('v'), ' (m²/d)',
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Compression index of Clay', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='c_v', type='number', value=5e-2, step=0.001, className='input-field'),                


                # Sand-2 Properties
                html.H3('Sand-2:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Sand-2', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_3', type='number', value=18, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Sand-2', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_3', type='number', value=19, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Sand-2', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_3', className='input-field')  
                ]),
               
            ]),
        ]),

        # Graphs container
        html.Div(className='graph-container', id='graphs-container', style={'display': 'flex', 'flexDirection': 'row', 'width': '75%'},
        children=[
            html.Div(style={'width': '40%', 'height': '100%'}, children=[
                dcc.Graph(id='soil-layers-graph', style={'height': '100%', 'width': '100%'})
            ]),
            html.Div(style={'width': '60%', 'height': '100%'}, children=[
                dcc.Graph(id='pressure-graph', style={'height': '100%', 'width': '100%'})
            ])
        ]),

        
        # Add the logo image to the top left corner
        html.Img(
            src='/assets/logo.png', className='logo',
            style={
                'position': 'absolute',
                'width': '15%',  # Adjust size as needed
                'height': 'auto',
                'z-index': '1000',  # Ensure it's on top of other elements
            }
        )
    ])
])

# Callback to control the bounderies of the input fields and sliders
@app.callback(
    [Output(f'gamma_prime_{i}', 'children') for i in range(1, 4)],
    Output('water-table', 'max'),
    [Input(f'gamma_r_{i}', 'value') for i in range(1, 4)],
    Input('z-1', 'value'),
    )
def update_gamma_prime(gamma_r1, gamma_r2, gamma_r3, z1):
    # Calculate γ′ as γ_r - 9.81 for each layer
    gamma_prime1 = round(gamma_r1 - 10, 2) if gamma_r1 is not None else None
    gamma_prime2 = round(gamma_r2 - 10, 2) if gamma_r2 is not None else None
    gamma_prime3 = round(gamma_r3 - 10, 2) if gamma_r3 is not None else None

    # water table max cannot be more than z1
    water_table_max = z1
    

    return f"= {gamma_prime1} kN/m³", f"= {gamma_prime2} kN/m³", f"= {gamma_prime3} kN/m³", water_table_max


# Callback to handle the animations and input updates
@app.callback(
    [Output('soil-layers-graph', 'figure'),
     Output('pressure-graph', 'figure')],
    [Input('update-button', 'n_clicks'), 
     Input('time-slider', 'value')],   
    [State('z-1', 'value'),
     State('z-2', 'value'),
     State('z-3', 'value'),
     State('delta_sigma', 'value'),
     State('gamma_1', 'value'),
     State('gamma_r_1', 'value'),
     State('gamma_2', 'value'),
     State('gamma_r_2', 'value'),
     State('gamma_3', 'value'),
     State('gamma_r_3', 'value'),
     State('c_v', 'value'),
     State('water-table', 'value')]
)

def update_graphs(n_clicks, t, z1, z2, z3, delta_sigma, gamma_1, gamma_r_1, gamma_2, gamma_r_2, 
                   gamma_3, gamma_r_3, c_v, water_table):
    # Constants
    gamma_water = 10 # kN/m³ for water

    # total depth
    total_depth = z1 + z2 + z3

    # Ensure y_top has a default value
    y_top = -0.1*total_depth

    # Define soil layers and their boundaries with specified patterns
    layers = [
        {'layer_id': '1', 'name': 'Sand-1', 'thickness' : z1,'top': 0, 'bottom': z1, 'color': 'rgb(244,164,96)','fillpattern': {'shape': '.'}, 
         'x0': -0.2,'text':'h\u2081'
         },  # Dots for Sand
        {'layer_id': '2', 'name': 'Clay', 'thickness' : z2, 'top': z1, 'bottom': z1 + z2, 'color': 'rgb(139,69,19)',
         'fillpattern': {'shape': ''}, 'x0': 0
         },  # Dashes for Clay
        {'layer_id': '3', 'name': 'Sand-2', 'thickness' : z3, 'top': z1 + z2, 'bottom': z1 + z2 + z3, 'color': 'rgb(244,164,96)',
         'fillpattern': {'shape': '.'}, 'x0': -0.70, 'text':'h\u2083'
         },  # Dots for Sand
    ]

    # Create the soil layers figure (139,69,19)
    soil_layers_fig = go.Figure()
    pressure_fig = go.Figure()

    for layer in layers:
        if layer['thickness'] > 0:
            soil_layers_fig.add_trace(go.Scatter(
                x=[0, 0, 1, 1],  # Create a rectangle-like shape
                y=[layer['top'], layer['bottom'], layer['bottom'], layer['top']],
                fill='toself',
                fillcolor=layer['color'],  # Transparent background to see the pattern
                line=dict(width=1, color='black'),
                name=layer['name'],
                showlegend=False,
                hoverinfo='skip',  # Skip the hover info for these layers
                fillpattern=layer['fillpattern']  # Use the specified fill pattern
            ))

            # Add a line at the top and bottom of each layer
            soil_layers_fig.add_trace(go.Scatter(
                x=[0, 1],  # Start at -1 and end at 1
                y=[layer['top'], layer['top']],  # Horizontal line at the top of the layer
                mode='lines',
                line=dict(color='black', width=1, dash='dash'),
                showlegend=False,  # Hide legend for these lines
                hoverinfo='skip'  # Skip the hover info for these line
            ))
            
            # Add the annotation for the layer name
            mid_depth = (layer['top'] + layer['bottom']) / 2  # Midpoint of the layer
            soil_layers_fig.add_annotation(
                x=0.4,  # Position the text slightly to the right of the layer box
                y=mid_depth,
                text=layer['name'],  # Layer name as text
                font = dict(size=14, color="white", weight='bold'),
                showarrow=False,  # Don't show an arrow
                xanchor='left',  # Anchor text to the left
                yanchor='middle'  # Center text vertically with the midpoint             
            )


    # Add a line at the water table
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 1],  # Start at -1 and end at 1
        y=[0, 0],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='blue', width=2, dash='dot'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    )) 

    # adding arrowas distributed load on the foundation
    num_arrows = 10
    for i in range(0, int(num_arrows+1)):
        soil_layers_fig.add_annotation(
            x=i*0.1, # x-coordinate of arrow head
            y=0, # y-coordinate of arrow head
            ax=i*0.1, # x-coordinate of tail
            ay=0.9*y_top, # y-coordinate of tail
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="black"
        )

    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 1],  
        y=[0, 0],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='black', width=4, dash='solid'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

    #  adding text for the load delta sigma
    soil_layers_fig.add_annotation(
        x=0.5,  # Position the text slightly to the right of the layer box
        y=y_top,
        text='Δσ',  # Layer name as text
        font = dict(size=14, color="black", weight='bold'),
        showarrow=False,  # Don't show an arrow
        xanchor='center',  # Anchor text to the left
        yanchor='middle'  # Center text vertically with the midpoint
    )
    # add a line for the water table
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 1],  # Start at -1 and end at 1
        y=[water_table, water_table],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='blue', width=2, dash='dot'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

   
    # First figure (soil_layers_fig)
    soil_layers_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title= dict(text='Width (m)', font=dict(weight='bold')),
        xaxis=dict(
            range=[0, 1],  # Adjusting the x-range as needed
                showticklabels=False,
                showgrid=False,
                title=None, 
                zeroline=False
        ),
        yaxis_title= dict(text='Depth (m)', font=dict(weight='bold')),
        yaxis=dict(
            range=[total_depth, y_top],  # Adjusted range for the y-axis (inverted for depth)
            showticklabels=True,
            ticks='outside',
            title_standoff=4,
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            zeroline=False,
            # scaleanchor="x",  # Link y-axis scaling with x-axis
            # scaleratio=1,
        ),
        # margin=dict(l=30, r=10, t=10, b=20),
    )

     # Calculate pore water pressure based on conditions
    step = 0.05
    z1_depth = np.linspace(0, z1, num=int(z1/step)+1)
    z2_depth = np.linspace(z1, z1+z2, num=int(z2/step)+1)
    z3_depth = np.linspace(z1+z2, z1+z2+z3, num=int(z3/step)+1)
    depths = np.concatenate((z1_depth, z2_depth, z3_depth))
    # depths = np.linspace(0, z1 + z2 + z3, num=int((z1 + z2 + z3)/step) + 1, endpoint=True)  # Define depths from 0 to total depth
    total_stress_z1 = np.zeros_like(z1_depth)
    total_stress_z2 = np.zeros_like(z2_depth)
    total_stress_z3 = np.zeros_like(z3_depth)
    pore_pressure_z1 = np.zeros_like(z1_depth)
    pore_pressure_z2 = np.zeros_like(z2_depth)
    pore_pressure_z3 = np.zeros_like(z3_depth)
    effective_stress_z1 = np.zeros_like(z1_depth)
    effective_stress_z2 = np.zeros_like(z2_depth)
    effective_stress_z3 = np.zeros_like(z3_depth)
   
    # print(depths)
    


    # Calculate pore pressure based on the conditions
  
    # condition for the first layer
    for i, depth in enumerate(z1_depth):
        
        if depth <= water_table:
            total_stress_z1[i] = depth * gamma_1 + delta_sigma
            pore_pressure_z1[i] = 0
        else:
            total_stress_z1[i] = total_stress_z1[int(water_table/step)] + (depth - water_table) * gamma_r_1
            pore_pressure_z1[i] = (depth-water_table) * gamma_water
        effective_stress_z1[i] = total_stress_z1[i] - pore_pressure_z1[i]

    # condition for the second layer
    for i, depth in enumerate(z2_depth):

        total_stress_z2[i] = total_stress_z1[int(z1/step)] + (depth - z1) * gamma_r_2
        # pore water pressure
        if depth - z1 <= 0.5*z2:
            H = depth-z1
        elif  depth-z1 > 0.5*z2 and depth-z1 < z2:
            H = z2-(depth-z1)
        
            
        t_99 = (1.4832*(z2/2)**2)/c_v

    
        T_v = ((t/100) * t_99* c_v)/(z2/2)**2

        if T_v >= 0 and  T_v < (1/12):
            U = np.sqrt(4*T_v/3)    
        else:
            U = 1 - (2/3)*np.exp((1/4)-(3*T_v))
        
        # Calculate excess pore pressure using the series sum
        M = np.pi/2 * (2 * np.arange(0, 100) + 1)  # Mode numbers
        excess_pore_pressure = (2 * delta_sigma / M) * np.sin(M * (depth - z1) / (z2/2)) * np.exp(-M**2 * T_v)
        excess_pore_pressure = np.sum(excess_pore_pressure)  # Sum up for all modes


        if t == 0:
            pore_pressure_z2[i] = (depth - water_table) * gamma_water + delta_sigma
        elif t == 100:
            pore_pressure_z2[i] = (depth - water_table) * gamma_water
        else:
            pore_pressure_z2[i] = (depth - water_table) * gamma_water + excess_pore_pressure
        effective_stress_z2[i] = total_stress_z2[i] - pore_pressure_z2[i]


    # condition for the third layer    
    for i, depth in enumerate(z3_depth):
        total_stress_z3[i] = total_stress_z2[int(z2/step)] + (depth+-z1-z2) * gamma_r_3
        pore_pressure_z3[i] = (depth-water_table) * gamma_water
        effective_stress_z3[i] = total_stress_z3[i] - pore_pressure_z3[i]

    # Combine the results for all layers
    total_stress = np.concatenate((total_stress_z1, total_stress_z2, total_stress_z3))
    pore_pressure = np.concatenate((pore_pressure_z1, pore_pressure_z2, pore_pressure_z3))
    effective_stress = np.concatenate((effective_stress_z1, effective_stress_z2, effective_stress_z3))


    # Create the pore pressure figure
    for layer in layers:
        # Add a line at the bottom of each layer other graph
        pressure_fig.add_trace(go.Scatter(
            x=[0, 1000],  # Start at -1 and end at 1
            y=[layer['bottom'], layer['bottom']],  # Horizontal line at the top of the layer
            mode='lines',
            line=dict(color='black', width=1, dash='dash'),
            showlegend=False,  # Hide legend for these lines
            hoverinfo='skip'  # Skip the hover info for these line
        ))
    
    
    

    pressure_fig.add_trace(go.Scatter(
        x=total_stress,
        y=depths,
        mode='lines',
        line=dict(color='red', width=3 ),
        name='Total Vertical Stress, σ<sub>T</sub>'
    ))

    pressure_fig.add_trace(go.Scatter(
        x=pore_pressure,
        y=depths,
        mode='lines',
        line=dict(color='blue', width=3 ),
        name='Pore Water Pressure, u'
    ))


    pressure_fig.add_trace(go.Scatter(
        x=effective_stress,
        y=depths,
        mode='lines',
        line=dict(color='green', width=3 ),
        name='Effective Vertical Stress, σ\''
    ))

    # draw the original pore water pressuer line
    pressure_fig.add_trace(go.Scatter
    (
        x=[0, (total_depth - water_table) * gamma_water],
        y=[0, total_depth],
        mode='lines',
        line=dict(color='blue', width=3, dash='dot'),
        name='Initial Pore Water Pressure, u<sub>0</sub>'
    ))

    pressure_fig.update_layout(
        xaxis_title=dict(text='Stress/pressure (kPa)', font=dict(weight='bold')),
        plot_bgcolor='white',
        xaxis=dict(
            range=[0, 1.2 * max(max(total_stress), max(pore_pressure), max(effective_stress))],
            side='top',
            title_standoff=4,
            zeroline=False,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".2f"  # Sets hover value format for x-axis to two decimal places
        ),
        yaxis_title=dict(text='Depth (m)', font=dict(weight='bold')),
        yaxis=dict(
            range=[total_depth, y_top],
            zeroline=True,
            zerolinecolor= "black",
            title_standoff=4,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".3f"  # Sets hover value format for y-axis to two decimal places
        ),
        legend=dict(
            yanchor="top",  # Align the bottom of the legend box
            y=1,               # Position the legend at the bottom inside the plot
            xanchor="right",    # Align the right edge of the legend box
            x=1,               # Position the legend at the right inside the plot
            font= dict(size=10),  # Adjust font size
            bgcolor="rgba(255, 255, 255, 0.7)",  # Optional: Semi-transparent white background
            bordercolor="black",                 # Optional: Border color
            borderwidth=1                        # Optional: Border width
        ),
        # margin=dict(l=30, r=10, t=10, b=20),
    )
    


    return soil_layers_fig, pressure_fig
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    

# Expose the server
server = app.server
