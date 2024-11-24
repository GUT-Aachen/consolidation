import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.title = 'Consolidation'
app._favicon = ('assets/favicon.ico')

# Updated layout with sliders on top and layer properties below
app.layout = html.Div([
    dcc.Store(id='window-width'),

    # Add the dcc.Interval component to track the window width
    dcc.Store(id='animation-time', data=0),  # Store for animation time
    dcc.Store(id='animation-active', data=False),  # Store for animation state (active/inactive)
    dcc.Interval(id='interval', interval=1000, n_intervals=0),
    # Main container
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'height': '100vh'}, children=[
    # Control container
    html.Div(
    id='control-container',
    children=[
        html.H1('Consolidation', className='h1'),

        html.Div(
            className='animation-container',
            children=[
                # Dropdown for soil type selection
                html.Div(
                    className='dropdown-container',
                    children=[
                        html.Label('Soil Type:', className='label-name'),
                        dcc.Dropdown(
                            id='soil-type-dropdown',
                            options=[
                                {'label': 'Cohesionless Soils', 'value': 'Cohesionless'},
                                {'label': 'Cohesive Soils', 'value': 'Cohesive'}
                            ],
                            value='Cohesionless',  # Default to dense sand/OC clay
                            clearable=False  # Prevents clearing the dropdown
                        ),
                    ]
                ),

                # Tap control
                html.Div(
                    className='tap-controller',
                    children=[
                        html.Label('Tap:', className='label-name'),
                        html.Button(
                            id='tap-button',
                            n_clicks=0,
                            children='Closed',  # Default text when tap is closed
                            className='tap-button'
                        ),
                    ]
                ),
                # Time slider control
                html.Div(
                    className='time-slider-container',
                    children=[
                        html.Label('Time:', className='label-name'),
                        dcc.Slider(
                            id='time-slider',
                            min=0,
                            max=100,  # Large number to represent "infinity"
                            step=1,
                            value=0,  # Default value (start at 0)
                            marks={0: '0', 100: '∞'},  # Mark 0 as "0" and 1000 as "∞"
                            tooltip=None,  # This hides the tooltip when the slider is moved
                            updatemode='drag'  # Ensures the slider updates as it's dragged
                        ),
                    ]
                ),
            ]
        ),

                # Equations container
                html.Div(
                    className='equations-container',
                    children=[
                        html.H3("Relevant Equations:", style={'textAlign': 'left'}),
                        # Uncomment and add specific equations if needed
                        # html.H3(children=[f'γ′  = γ', html.Sub('sat'),  ' - γ', html.Sub('w')], style={'textAlign': 'left'}),
                        # html.H3(children=[f'γ*  = γ′ ± (Δh/ΔL)γ', html.Sub('w')], style={'textAlign': 'left'}),
                        # html.H3(children=[f'Δσ = γ*Δz'], style={'textAlign': 'left'}),
                    ]
                ),
            ]
        ),

        # Graphs container
        html.Div(className='graph-container', id='graphs-container', style={'display': 'flex', 'flexDirection': 'row', 'width': '80%'}, children=[
            html.Div(style={'width': '60%', 'height': '100%'}, children=[
                dcc.Graph(id='boxes-illustartions-container', style={'height': '100%', 'width': '100%'})
            ]),
            html.Div(style={'width': '40%', 'height': '100%'}, children=[
                dcc.Graph(id='stress-time-container', style={'height': '100%', 'width': '100%'})
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

@app.callback(
    [Output('tap-button', 'children'),
     Output('tap-button', 'className'),
     Output('animation-active', 'data')],
    [Input('tap-button', 'n_clicks')],
    [State('animation-active', 'data')],
)
def toggle_tap(n_clicks, animation_active):
    if n_clicks % 2 == 0:
        return 'Closed', 'tap-button', False  # Tap is closed, animation stops
    else:
        return 'Opened', 'tap-button open', True  # Tap is opened, start animation
    
# JavaScript for updating window width
app.clientside_callback(
    """
    function(n_intervals) {
        return window.innerWidth;
    }
    """,
    Output('window-width', 'data'),
    Input('interval', 'n_intervals')
)


# Callback to handle the animations and input updates
@app.callback(
    [Output('boxes-illustartions-container', 'figure'),
     Output('stress-time-container', 'figure'),
     Output('animation-time', 'data')
    ],

    [Input('tap-button', 'children'),
    #  Input('soil-type-dropdown', 'value'),
     Input('interval', 'n_intervals')
    ],
    [State('animation-time', 'data'),
     State('animation-active', 'data'),
     State('soil-type-dropdown', 'value')]
)
def update_graphs(tap_state, n_intervals, current_time, animation_active, soil_type_state):
 
    boxes_iilu_fig = go.Figure()
    stress_t_fig = go.Figure()

    boxes = [{'id':'spring', 'x0':0, 'x1':60, 'y0':0, 'y1':60}, 
             {'id':'particles', 'x0':0, 'x1':60, 'y0':90, 'y1':150}
            ]
    
    
    for box in boxes:
        # First add the spring lines if it's the spring box
        if box['id'] == 'spring':
            boxes_iilu_fig.add_layout_image(
                dict(
                    source='/assets/spring.png',  # Your image path
                    xref="x", yref="y",
                    x=0.8*((box['x1']-box['x0'])/2),
                    y=box['y0'] + (0.8*(box['y1'] - box['y0'])),  # Align to the top of the rectangle
                    sizex=0.2*((box['x1']-box['x0'])),  # Width matching the rectangle
                    sizey=box['y0'] + (0.8*(box['y1'] - box['y0'])) - box['y0'],  # Height matching the rectangle
                    xanchor="left",
                    yanchor="top",
                    layer="below",  # Ensure the image is behind everything
                    sizing="stretch"
                )
            )
        #     # Draw a spring-like pattern in the center
        #     num_loops = 10  # Adjust for more or fewer loops
        #     mid_x = (box['x0'] + box['x1']) / 2  # Center x-position
        #     amplitude = 0.05 * (box['x1'] - box['x0'])  # Adjust amplitude for appearance
        #     y0 = box['y0']
        #     dy = 0.5*((0.8 * box['y1'] - box['y0']) / num_loops)  # Height increment for each loop

        #     for i in range(num_loops):
        #         y1 = y0 + dy
        #         # Create one line from left to right, then from right to left (alternating)
        #         boxes_iilu_fig.add_shape(
        #             type="line",
        #             x0=mid_x - amplitude, y0=y0,
        #             x1=mid_x + amplitude, y1=y1,
        #             line=dict(color="black", width=5),
        #             layer='below'
        #         )
        #         y0 += dy
        #         y1 = y0 + dy
        #         boxes_iilu_fig.add_shape(
        #             type="line",
        #             x0=mid_x + amplitude, y0=y0,
        #             x1=mid_x - amplitude, y1=y1,
        #             line=dict(color="black", width=5),
        #             layer='below'
        #         )
        #         y0 += dy  # Increment y0 for the next loop

        # Then add the rectangles and other traces
        boxes_iilu_fig.add_trace(go.Scatter( 
            x=[box['x0'], 1.05*box['x1'], 1.05*box['x1'], box['x1'], box['x1'], box['x0']],  # Draw rectangle as a closed loop
            y=[box['y0'], box['y0'], box['y0'] + 0.05*(box['y1'] - box['y0']), box['y0'] + 0.05*(box['y1'] - box['y0']), box['y0'] + (0.8*(box['y1'] - box['y0'])), box['y0'] + (0.8*(box['y1'] - box['y0']))],
            fill='toself',
            fillcolor='lightskyblue',
            opacity=0.6,
            line=dict(color='black', width=0, dash='solid'),
            mode='lines',  # Ensure it's only lines, no markers
            showlegend=False,  # Hide legend for these lines
            hoverinfo='skip',
        ))

        if box['id'] == 'particles':
            boxes_iilu_fig.add_layout_image(
                dict(
                    source='/assets/soil_particles.png',  # Your image path
                    xref="x", yref="y",
                    x=box['x0'],
                    y=box['y0'] + (0.8*(box['y1'] - box['y0'])),  # Align to the top of the rectangle
                    sizex=box['x1'] - box['x0'],  # Width matching the rectangle
                    sizey=box['y0'] + (0.8*(box['y1'] - box['y0'])) - box['y0'],  # Height matching the rectangle
                    xanchor="left",
                    yanchor="top",
                    layer="below",  # Ensure the image is behind everything
                    sizing="stretch"
                )
            )
        
        # Add multiple load arrows along the top of each box
        num_arrows = 10  # Define how many arrows you want on top of the rectangle
        arrow_spacing = (box['x1'] - box['x0']) / (num_arrows + 1)  # Evenly space the arrows

        for i in range(1, num_arrows + 1):
            # Calculate the x position of each arrow
            arrow_x = box['x0'] + i * arrow_spacing
            top_y = box['y0'] + (0.8 * (box['y1'] - box['y0']))  # Top of the rectangle

            # Add each arrow pointing down
            boxes_iilu_fig.add_annotation(
                x=arrow_x,  # Position of the arrow
                y=top_y,  # Start at the top of the rectangle
                ax=arrow_x,  # Arrow tip at the same x (vertical arrow)
                ay=top_y + 10,  # 10 units downward for the arrow tip
                axref="x", ayref="y",
                xref="x", yref="y",
                showarrow=True,
                arrowhead=2,  # Arrowhead style
                arrowsize=1,  # Arrow size
                arrowcolor="red",  # Red color for the arrow
                arrowwidth=2  # Set arrow line width
            )

        # Add a single text annotation for all arrows
        mid_x = (box['x0'] + box['x1']) / 2  # Center of the box for the text
        top_y = box['y0'] + (0.8 * (box['y1'] - box['y0']))  # Top of the rectangle
        boxes_iilu_fig.add_annotation(
            x=mid_x,  # Position at the center of the rectangle
            y=top_y + 11,  # Place a little above the arrows
            text="Δσ",  # Text label
            showarrow=False,  # No arrow for the text
            font=dict(size=22, color="black", family="Arial", weight="bold"),  # Bold text
            align="center"
        )

        # Add left, right, and bottom lines (these will appear on top of the spring lines)
        boxes_iilu_fig.add_shape(
            type='line',  # Create a line
            x0=box['x0'],  x1=box['x0'],  # Start and end points
            y0=box['y0'],  y1=box['y1'],  # Start and end points
            line=dict(color='black', width=5, dash='solid'),
        )

        boxes_iilu_fig.add_shape(
            type='line',  # Create a line
            x0=box['x1'],  x1=box['x1'],  # Start and end points
            y0=box['y0'] + 0.05*(box['y1'] - box['y0']),  y1=box['y1'],  # Start and end points
            line=dict(color='black', width=5, dash='solid'),
        )

        boxes_iilu_fig.add_shape(
            type='line',  # Create a line
            x0=box['x0'],  x1=1.1*box['x1'],  # Start and end points
            y0=box['y0'],  y1=box['y0'],  # Start and end points
            line=dict(color='black', width=5, dash='solid'),
        )

        # add the tap channel
        boxes_iilu_fig.add_shape(
            type='line',  # Create a line
            x0=box['x1'],  x1=1.1*box['x1'],  # Start and end points
            y0=box['y0'] + 0.05*(box['y1'] - box['y0']),  y1=box['y0'] + 0.05*(box['y1'] - box['y0']),  # Start and end points
            line=dict(color='black', width=5, dash='solid'),
        )

        # add the tap cross
        boxes_iilu_fig.add_shape(
            type='line',  # Create a line
            x0=1.02*box['x1'],  x1=1.08*box['x1'],  # Start and end points
            y0=box['y0']-1 ,  y1=box['y0'] + 0.05*(box['y1'] - box['y0']) + 1,  # Start and end points
            line=dict(color='black', width=6, dash='solid'),
        )
        boxes_iilu_fig.add_shape(
            type='line',  # Create a line
            x1=1.02*box['x1'],  x0=1.08*box['x1'],  # Start and end points
            y0=box['y0']-1 ,  y1=box['y0'] + 0.05*(box['y1'] - box['y0']) + 1,  # Start and end points
            line=dict(color='black', width=6, dash='solid'),
        )

        # add the tap circle
        boxes_iilu_fig.add_shape(
            type='circle',  # Create a line
            x0=1.04*box['x1'],  x1=1.06*box['x1'],  # Start and end points
            y0=box['y0']-0.5 ,  y1=box['y0'] + 0.05*(box['y1'] - box['y0']) + 0.5,  # Start and end points
            line=dict(color='black', width=4, dash='solid'),
            # fillcolor='black',
        )

        # Add a text annotation for the tap
        boxes_iilu_fig.add_annotation(
            x=1.05*box['x1'],  # Position at the center of the rectangle
            y=box['y0'] + 0.05*(box['y1'] - box['y0']) + 5,  # Place a little above the arrows
            text="Tap",  # Text label
            showarrow=False,  # No arrow for the text
            font=dict(size=20, color="black", family="Arial", weight="bold"),  # Bold text
            align="center"
        )


    # add arrow between the two boxes
    boxes_iilu_fig.add_annotation(
        x=boxes[1]['x1']/2,  # Position of the arrow
        y=boxes[1]['y0'] - 20,  # Start at the top of the rectangle
        ax=boxes[1]['x1']/2,  # Arrow tip at the same x (vertical arrow)
        ay=boxes[1]['y0'] - 5,  # 10 units downward for the arrow tip
        axref="x", ayref="y",
        xref="x", yref="y",
        showarrow=True,
        arrowhead=3,  # Arrowhead style
        arrowsize=1,  # Arrow size
        arrowcolor="rgb(0,84,159)",  # Red color for the arrow
        arrowwidth=5  # Set arrow line width
    )

    boxes_iilu_fig.update_layout(
        # title=dict(
        # text='Soil Layers',
        # x=0.4,  # Center the title horizontally
        # y=0.95,  # Position the title above the plot area
        # xanchor='right',
        # yanchor='top',
        # font=dict(size=20)  # Adjust the font size as needed
        # ),
        plot_bgcolor='white',
        xaxis=dict(
            range=[-2, 100],  
            showticklabels=False,
            showgrid=False,
            title=None, 
            zeroline=False,
            fixedrange=True
            ),
        yaxis_title='Depth (m)',
        yaxis=dict(
            range=[-2, 150],  
            showticklabels=False,
            showgrid=False,
            title=None, 
            zeroline=False,
            fixedrange=True
            ),
        margin=dict(l=10, r=0, t=30, b=10)  # Adjust margins to reduce space around the plot
    )

    stress_t_fig.update_layout(
        plot_bgcolor='white',
        xaxis = dict(
            range=[0, 1],  
            showticklabels=False,
            showgrid=False,
            title=None, 
            zeroline=False,
            fixedrange=True
            ),
        yaxis_title='Depth (m)',
        yaxis=dict(
            range=[0, 1.3],  
            showticklabels=False,
            showgrid=False,
            title=None, 
            zeroline=False,
            fixedrange=True
            ),
        margin=dict(l=0, r=10, t=30, b=10)  # Adjust margins to reduce space around the plot
    )

    return boxes_iilu_fig, stress_t_fig, current_time

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    

# Expose the server
server = app.server
