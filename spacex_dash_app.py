import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                    ],
                                    value='ALL',  
                                    placeholder="Select a Launch Site here",
                                    searchable=True  
                                ),
                                html.Br(),

                      
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i} Kg' for i in range(0, 10001, 1000)},
                                    value=[min_payload, max_payload]
                                ),

  
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_df = spacex_df[spacex_df['class'] == 1]


        site_success_counts = success_df.groupby('Launch Site').size().reset_index(name='counts')

        fig = px.pie(
            site_success_counts,
            names='Launch Site',
            values='counts',
            title='Total Success Launches By Site'
        )
    else:

        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Launch Success vs. Failure for {entered_site}',
            labels={'class': 'Launch Outcome'},
            color='class',
            color_discrete_map={0: 'red', 1: 'green'}
        )

    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    filtered_df = spacex_df
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    filtered_df = filtered_df[filtered_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Launch Success vs. Payload Mass',
        labels={'class': 'Launch Success', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    return fig

if __name__ == '__main__':
    app.run_server()
