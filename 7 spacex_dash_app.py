import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Dropdown list for Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            ],
                                        value='ALL',
                                        placeholder="Select a Launch Site here",
                                        searchable=True
                                        ),
                                html.Br(),

                                # Pie chart showing successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Payload range slider
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0 Kg',
                                                    2000: '2000 Kg',
                                                    4000: '4000 Kg',
                                                    6000: '6000 Kg',
                                                    8000: '8000 Kg',
                                                    10000: '10000 Kg'},
                                                value=[min_payload, max_payload]),

                                # Scatter chart for payload vs. launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Callback function for pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    all_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(all_df, values='class', 
        names = 'Launch Site', 
        title = 'Rate of Successful Launches By Site')
        return fig
    else:
        spec_df = spacex_df.loc[spacex_df['Launch Site'] == entered_site].groupby(['Launch Site','class']).size().reset_index(name='counts')
        
        l_success = spec_df['counts'][1]
        l_failure = spec_df['counts'][0]    
        fig = px.pie(spec_df, values=[l_success, l_failure], names=['Success', 'Failure'],
               title="Successful Launch Rate for Site " + entered_site)
        return fig

# Callback function for scatter plot
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, entered_payload):
    spec_df = spacex_df[spacex_df['Payload Mass (kg)'].between(entered_payload[0],entered_payload[1])]

    if entered_site == 'ALL':
        fig = px.scatter(spec_df,
        x = 'Payload Mass (kg)',
        y='class',
        color = "Booster Version Category",
        title = 'Correlation Between Payload and Success for All Sites')
        return fig
    else:
        fig = px.scatter(spec_df.loc[spec_df['Launch Site'] == entered_site],
        x = 'Payload Mass (kg)',
        y='class',
        color = 'Booster Version Category',
        title = 'Correlation between Payload and Success for Site ' + entered_site)
        return fig


if __name__ == '__main__':
    app.run_server()
