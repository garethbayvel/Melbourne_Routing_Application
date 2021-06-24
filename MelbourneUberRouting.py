import pandas as pd
import numpy as np

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import *
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot

from dash import no_update
import dash
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

weekdays_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

pedestrian_df = pd.read_pickle("Compressed_Pickled_Melbourne_pedestrian.pkl",compression='bz2')
plotting_df = pd.read_pickle("Compressed_revised_plotting.pkl",compression='bz2')


# Scattermapbox will not read our lat and lon if they are not contained in this form so we have to repeat this step again
plotting_df['Latitude'] = plotting_df['Latitude'].str.replace("\'", '').str.replace(r"[", '', regex=True).str.replace(
    r"]", '', regex=True).str.strip()
plotting_df['Longitude'] = plotting_df['Longitude'].str.replace("\'", '').str.replace(r"[", '', regex=True).str.replace(
    r"]", '', regex=True).str.strip()


def making_float(df, column):
    lat = []
    for x in range(0, len(df)):
        final_coord = [*map(float, df[column][x].split(','))]
        lat.append(final_coord)
    return lat


lat = making_float(plotting_df, 'Latitude')
lon = making_float(plotting_df, 'Longitude')

plotting_df['Latitude'] = lat
plotting_df['Longitude'] = lon


app.layout = html.Div([
    # creating Dash header
    html.Div([
        html.H1(
            children='MELBOURNE UBER MAP')

        ############################################################################################
        # Creating radio items
    ]),
    html.Div([
        dcc.RadioItems(
            id='map-id',
            options=[{'label': i, 'value': i} for i in ['Uber', 'Pedestrian']],
            value='Pedestrian',
            labelStyle={'display': 'inline-block'}
        )
    ]),
    ############################################################################################
    # Dropdown for user input source

    html.Div([' Source: ',
              dcc.Dropdown(
                  id='source-drop',
                  options=[{'label': i, 'value': i} for i in plotting_df['Source_road'].unique()],
                  value=plotting_df['Source_road'].unique()[0]
              )
              ],
             style={'width': '33%', 'display': 'inline-block'}
             ),
    ############################################################################################
    # Dropdown for user input destination

    html.Div([' Destination: ',
              dcc.Dropdown(
                  id='destination-drop',
                  options=[{'label': i, 'value': i} for i in plotting_df['Destination_road'].unique()],
                  value=plotting_df['Destination_road'].unique()[0]
              )
              ],
             style={'width': '33%', 'display': 'inline-block',
                    'padding': 2.2, 'marginBottom': 30}
             ),
    ############################################################################################
    # Dropdown for day of week

    html.Div(['Day of Week',
              dcc.Dropdown(
                  id='weekday-drop',
                  options=[{'label': i, 'value': i} for i in weekdays_order],
                  value='Monday'
              ),
              dcc.RadioItems(
                  id='dist-marginal',
                  labelStyle={'display': 'inline-block', 'marginTop': '5px', 'text-align': 'center'},
                  options=[{'label': x, 'value': x}
                           for x in ['Bar', 'Box']],
                  value='Bar'),
              ], style={'width': '33%', 'display': 'inline-block', 'padding': 2.2, 'float': 'right'}
             ),
    ############################################################################################
    # Initializing our first graph which is our Scattermapbox

    html.Div([
        dcc.Graph(id='graph-with-slider')
    ], style={'display': 'inline-block', 'width': '65%', 'marginBottom': 20}
    ),
    ################################################################################################
    # Initializing our second and third graphs which are our barchart and heatmap

    html.Div([
        dcc.Graph(id='bar-plot'),
        dcc.Graph(id='heatmap'),
        dcc.RadioItems(
            id='covid-id',
            labelStyle={'display': 'inline-block', 'text-align': 'center'},
            options=[{'label': x, 'value': x}
                     for x in ['Heatmap', 'Covid-Bar']],
            value='Heatmap')
    ], style={'width': '33%', 'display': 'inline-block', 'padding': 0.5, 'float': 'right'}
    ),
    ############################################################################################
    # Our month slider appears below our graphs
    html.Div(['Month',
              dcc.Slider(
                  id='month-slider',
                  min=plotting_df['month'].min(),
                  max=plotting_df['month'].max(),
                  value=plotting_df['month'].min(),
                  marks={str(month): str(month) for month in plotting_df['month'].unique()},
                  step=None)
              ])
])


###########################################################################################################
# SOURCE DROPDOWN UPDATE

@app.callback(
    Output('source-drop', 'options'),
    Output('source-drop', 'value'),
    Input('map-id', 'value')
)
# Depending on Uber or Pedestrian selection we want our street names to change accordingly
def update_source_dropdown(source):
    pedestrians = pedestrian_df.sort_values(by=['Sensor_Name']).copy()
    if source == 'Pedestrian':
        return list(([{'label': i, 'value': i} for i in pedestrians['Sensor_Name'].unique()],
                     pedestrians['Sensor_Name'].unique()[0]))
    else:
        plotting_df['Suburb'] = plotting_df['Source_road'].str.split(',').str[-1]
        sorting_source = dict(zip(plotting_df['Source_road'], plotting_df['Suburb']))

        sorted_dict = {}
        sorted_keys = sorted(sorting_source, key=sorting_source.get)  # Sorting our Source names by Suburb

        for w in sorted_keys:
            sorted_dict[w] = sorting_source[w]
        return list(([{'label': x, 'value': x} for x in sorted_keys],
                     sorted_keys[0]))


###########################################################################################################
# DESTINATION DROPDOWN UPDATE


@app.callback(
    Output('destination-drop', 'options'),
    Output('destination-drop', 'value'),
    Input('source-drop', 'value'),
    Input('map-id', 'value'),

)
# Depending on our source selection we want to only be able to select matched destinations with that source
def update_destination_dropdown(source, selected_map):
    if selected_map == 'Uber':
        destination_options = plotting_df[plotting_df.Source_road == source]

        # creating a list all of the destinations that match the selected source
        destination_list = set(zip(destination_options['Source_road'], destination_options['Destination_road']))
        Destination = []
        for x in range(0, len(destination_list)):
            Destination.append(list(destination_list)[x][1])  # append only the destination to the list

        # creating a list of suburb names that are apart of the destination string i.e Flinders, "Melbourne"
        suburb = [x.split(',')[-1] for x in Destination]
        zipped = dict(zip(Destination, suburb))
        sorted_destination = sorted(zipped, key=zipped.get)  # sorting our destinations by suburb
        return list(([{'label': i, 'value': i} for i in sorted_destination],
                     sorted_destination[0]))
    else:
        pedestrians = pedestrian_df[pedestrian_df.Sensor_Name == source].sort_values(by='Year').copy()
        return list(([{'label': x, 'value': x} for x in pedestrians['Year'].unique()],
                     pedestrians['Year'].unique()[0]))

    ###########################################################################################################
    # WEEKDAY DROPDOWN UPDATE


@app.callback(
    Output('weekday-drop', 'options'),
    Output('weekday-drop', 'value'),
    Input('source-drop', 'value'),
    Input('destination-drop', 'value'),
    Input('map-id', 'value')
)
# Depdning on our source and destination selection we need to ensure our weekdays update accordingly to available data
def update_weekday_dropdown(selected_source, selected_destination, selected_map):
    if selected_map == 'Uber':
        weekday_options = plotting_df[(plotting_df.Source_road == selected_source) &
                                      (plotting_df.Destination_road == selected_destination)].sort_values(
            by='N_weekday').copy()

        return list(([{'label': i, 'value': i} for i in weekday_options['Day_name'].unique()],
                     weekday_options['Day_name'].unique()[0]))
    else:
        pedestrians = pedestrian_df[(pedestrian_df['Sensor_Name'] == selected_source) &
                                    (pedestrian_df['Year'] == selected_destination)].sort_values(by=['N_Day']).copy()
        return list(([{'label': x, 'value': x} for x in pedestrians['Day'].unique()],
                     pedestrians['Day'].unique()[0]))

    ########################################################################################################
    # MONTH SLIDER UPDATE


@app.callback(
    [Output('month-slider', 'marks'),
     Output('month-slider', 'min'),
     Output('month-slider', 'max'),
     Output('month-slider', 'value')],
    Input('source-drop', 'value'),
    Input('destination-drop', 'value'),
    Input('weekday-drop', 'value'),
    Input('map-id', 'value'))
# Our month slider must update according to our slected map
def update_slider(selected_source, selected_destination, selected_weekday, selected_map):
    pedestrians = pedestrian_df[(pedestrian_df['Sensor_Name'] == selected_source) &
                                (pedestrian_df['Year'] == selected_destination) &
                                (pedestrian_df['Day'] == selected_weekday)]
    if selected_map == 'Pedestrian':
        return list(({str(i): str(i) for i in pedestrians['N_Month'].unique()},
                     pedestrians['N_Month'].min(),
                     pedestrians['N_Month'].max(),
                     pedestrians['N_Month'].min()))
    else:
        filtered_df = plotting_df[(plotting_df.Day_name == selected_weekday) &
                                  (plotting_df.Source_road == selected_source) &
                                  (plotting_df.Destination_road == selected_destination)].copy()

        return list(({str(x): str(x) for x in filtered_df['month'].unique()},
                     filtered_df['month'].min(),
                     filtered_df['month'].max(),
                     filtered_df['month'].min()))

    ########################################################################################################
    # CHLOROPLETH MAP


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('source-drop', 'value'),
    Input('destination-drop', 'value'),
    Input('month-slider', 'value'),
    Input('weekday-drop', 'value'),
    Input('map-id', 'value'))
# Conditional updates based upon whick map we select, uber or pedestrian for our chloropleth map
def update_figure(selected_source, selected_destination, selected_month, selected_weekday, selected_map):
    filtered_df = plotting_df[(plotting_df.month == selected_month) &
                              (plotting_df.Day_name == selected_weekday) &
                              (plotting_df.Source_road == selected_source) &
                              (plotting_df.Destination_road == selected_destination)].copy()

    # creating mean,min and max travel times to be used for our hovertext
    travel_mean = np.mean(filtered_df['mean_travel_time']) / 60
    travel_min = np.min(filtered_df['mean_travel_time']) / 60
    travel_max = np.max(filtered_df['mean_travel_time']) / 60
    travel_std = np.max(filtered_df['standard_deviation_travel_time']) / 60

    # we need our map to zoom in on the location that correspond to the source lat and lon
    filtered_df.reset_index(drop=True, inplace=True)
    center = filtered_df.head(2)
    latitude = center['Source_lat'].astype(float)
    longitude = center['Source_lon'].astype(float)

    # Initializing our Mapbox token so we can have nice map features
    MAPBOX_ACCESSTOKEN = ''
    plotly.express.set_mapbox_access_token(MAPBOX_ACCESSTOKEN)

    if selected_map == 'Uber':
        fig = go.Figure()

        fig.add_trace(go.Scattermapbox(
            name='Expected Travel Time in Min',
            mode="markers+lines",
            lon=filtered_df['Longitude'][0],
            lat=filtered_df['Latitude'][0],
            marker={'size': 0},
            line=dict(width=2, color='blue'),
            hovertemplate=f'<i>Mean</i>: {travel_mean:.2f} <br><b>Min</b>: {travel_min:.2f}<br>Max<b>:{travel_max:.2f}</b><br><b>Std</b>: {travel_std:.2f}',
        ))
        # adding source marker
        fig.add_trace(go.Scattermapbox(
            name="Source",
            mode="markers",
            lon=[filtered_df['Source_lon'][0]],
            lat=[filtered_df['Source_lat'][0]],
            marker={'size': 8, 'color': "red"}))

        # adding destination marker
        fig.add_trace(go.Scattermapbox(
            name="Destination",
            mode="markers",
            lon=[filtered_df['Destination_lon'][0]],
            lat=[filtered_df['Destination_lat'][0]],
            marker={'size': 8, 'color': 'green'}))

        fig.update_layout(
            showlegend=False,
            mapbox={
                'accesstoken': MAPBOX_ACCESSTOKEN,
                'center': dict(
                    lat=latitude.iloc[0],
                    lon=longitude.iloc[0]),
                'style': 'light',
                'zoom': 9})
        fig.update_layout(margin={'l': 0, 'b': 0, 'r': 10, 't': 0})

    # Conditional updates based upon whick map we select, uber or pedestrian for our chloropleth map
    else:
        pedestrians = pedestrian_df[(pedestrian_df.N_Month == selected_month) &
                                    (pedestrian_df.Sensor_Name == selected_source) &
                                    (pedestrian_df.Year == selected_destination) &
                                    (pedestrian_df.Day == selected_weekday)].copy()

        count_mean = np.array([np.mean(pedestrians['Hourly_Counts'])] * len(pedestrians))
        count_min = np.array([np.min(pedestrians['Hourly_Counts'])] * len(pedestrians))
        count_max = np.array([np.max(pedestrians['Hourly_Counts'])] * len(pedestrians))

        fig = px.scatter_mapbox(pedestrians, lat='lat', lon='lon',
                                hover_name='Sensor_Name',
                                color="Hourly_Counts", size="Hourly_Counts",
                                custom_data=["Hourly_Counts",
                                             count_mean,
                                             count_min,
                                             count_max],
                                color_continuous_scale=px.colors.cyclical.IceFire,
                                size_max=15,
                                zoom=13)

        fig.update_traces(
            hovertemplate="<br>".join([
                "Count: %{customdata[0]}",
                "Mean: %{customdata[1]}",
                "Min: %{customdata[2]}",
                "Max: %{customdata[3]}",

            ])
        )

        fig.update_layout(
            mapbox={
                'accesstoken': MAPBOX_ACCESSTOKEN,
                'center': dict(
                    lat=-37.8136,
                    lon=144.9631),
                'style': 'light',
                'zoom': 12})
        fig.update_layout(margin={'l': 0, 'b': 0, 'r': 0, 't': 0})

    return fig

    ########################################################################################################
    # BAR CHART


@app.callback(
    Output('bar-plot', 'figure'),
    Input('source-drop', 'value'),
    Input('destination-drop', 'value'),
    Input('month-slider', 'value'),
    Input('weekday-drop', 'value'),
    Input('map-id', 'value'),
    Input('dist-marginal', 'value'))
# creating our barchart with conditional statements
def update_bar_chart(selected_source, selected_destination, selected_month, selected_weekday, selected_map,
                     selected_plot):
    filtered_bar = plotting_df[(plotting_df.month == selected_month) &
                               (plotting_df.Day_name == selected_weekday) &
                               (plotting_df.Source_road == selected_source) &
                               (plotting_df.Destination_road == selected_destination)].copy()

    filtered_bar['Times'] = filtered_bar['start_hour'].astype(str) + "-" + filtered_bar['end_hour'].astype(str)

    filtered_bars = filtered_bar.groupby('Times').mean()[
        ['mean_travel_time', 'standard_deviation_travel_time']].reset_index()

    # if map is Uber and we have selected Bar then plot a Bar plot from the filtered data below
    if selected_map == 'Uber' and selected_plot == 'Bar':
        graph = px.bar(filtered_bars, x='Times', y=[np.round(filtered_bars['mean_travel_time'] / 60, 2),
                                                    np.round(filtered_bars['standard_deviation_travel_time'] / 60, 2)],
                       title="Bar Travel Time By Binned Hours",
                       category_orders={
                           "Times": ["0-7", "7-10", "10-16", "16-19", "19-0"]},
                       labels={'Times': 'Hours of The Day',
                               'value': 'Mean Time in Minutes'},
                       opacity=0.9
                       )

        graph.update_layout(height=225, margin={'l': 20, 'b': 10, 'r': 10, 't': 30},
                            coloraxis_showscale=False, showlegend=False,
                            font=dict(size=10))

    # if map is Uber and we have selected box then plot a box plot from the filtered data below
    elif selected_map == 'Uber' and selected_plot == 'Box':
        graph = px.box(filtered_bar, x='Times', y=np.round(filtered_bar['mean_travel_time'] / 60, 2),
                       title="Box Travel Time By Binned Hours",
                       color='Times',
                       category_orders={
                           "Times": ["0-7", "7-10", "10-16", "16-19", "19-0"]},
                       labels={'Times': 'Hours of The Day',
                               'y': 'Mean Time in Minutes'},
                       )
        graph.update_layout(height=225, margin={'l': 20, 'b': 10, 'r': 10, 't': 30},
                            coloraxis_showscale=False, showlegend=False,
                            font=dict(size=10))


    # if map is pedestrian and we have selected box then plot a box plot from the filtered data below
    elif selected_map == 'Pedestrian' and selected_plot == 'Box':
        pedestrians = pedestrian_df[(pedestrian_df.N_Month == selected_month) &
                                    (pedestrian_df.Year == selected_destination) &
                                    (pedestrian_df.Sensor_Name == selected_source) &
                                    (pedestrian_df.Day == selected_weekday)].copy()

        graph = px.box(pedestrians, x='Time', y='Hourly_Counts',
                       title="Pedestrian Hourly Count",
                       color='Time',
                       labels={'Time': 'Hours of The Day',
                               'Hourly_Counts': 'Pedestrian Count'}
                       )

        graph.update_layout(height=225, margin={'l': 20, 'b': 10, 'r': 10, 't': 30},
                            coloraxis_showscale=False,
                            font=dict(size=10),
                            showlegend=False)

    # if map is not uber and box is not slected then plot Bar base don filtered data below
    else:
        pedestrians = pedestrian_df[(pedestrian_df.N_Month == selected_month) &
                                    (pedestrian_df.Year == selected_destination) &
                                    (pedestrian_df.Sensor_Name == selected_source) &
                                    (pedestrian_df.Day == selected_weekday)].copy()

        pedestrian_bar = pedestrians.groupby('Time').mean()['Hourly_Counts'].reset_index()

        graph = px.bar(pedestrian_bar, x='Time', y='Hourly_Counts',
                       title="Pedestrian Hourly Count",
                       color='Hourly_Counts',
                       # category_orders={
                       # "Times": ["0-7", "7-10", "10-16", "16-19","19-0"]},
                       labels={'Time': 'Hours of The Day',
                               'Hourly_Counts': 'Pedestrian Count'}
                       )

        graph.update_layout(height=225, margin={'l': 20, 'b': 10, 'r': 10, 't': 30},
                            coloraxis_showscale=False,
                            font=dict(size=10))

    return graph

    ########################################################################################################
    # HEATMAP


@app.callback(
    Output('heatmap', 'figure'),
    Input('source-drop', 'value'),
    Input('destination-drop', 'value'),
    Input('month-slider', 'value'),
    Input('covid-id', 'value'),
    Input('map-id', 'value'))
# creating our heatmap
def update_heatmap(selected_source, selected_destination, selected_month, selected_covid, selected_map):
    filtered_heatmap = plotting_df[(plotting_df.Source_road == selected_source) &
                                   (plotting_df.Destination_road == selected_destination) &
                                   (plotting_df.month == selected_month)].copy()

    filtered_heatmap['Times'] = filtered_heatmap['start_hour'].astype(str) + "-" + filtered_heatmap['end_hour'].astype(
        str)

    filtered_heatmap = filtered_heatmap.groupby(['Day_name', 'Times']).mean()['mean_travel_time'].reset_index()
    filtered_heatmap['sort-axis'] = filtered_heatmap['Times'].str.extract('([\d]+)', expand=False).astype(int)
    filtered_heatmap = filtered_heatmap.sort_values(by=['sort-axis'])

    # if map is Uber then plot a heatmap plot from the filtered data below
    if selected_map == 'Uber':
        heat = go.Figure()
        heat.add_trace(go.Heatmap(
            z=np.round(filtered_heatmap['mean_travel_time'] / 60, 2),
            x=filtered_heatmap['Times'],
            y=filtered_heatmap['Day_name'],
            colorscale='Magma'
        ))

        heat.update_layout(height=225, margin={'l': 0, 'b': 0, 'r': 10, 't': 30},
                           title='Binned Hours and Days of Week Heatmap',
                           xaxis_nticks=5,
                           font=dict(size=10), title_font_color="black",
                           yaxis_title="Weekdays",
                           xaxis_title="Binned Time"
                           )


    # if map is Pedestrian and we have selected Covid-Bar then plot a facet bar plot from the filtered data below
    elif selected_map == 'Pedestrian' and selected_covid == 'Covid-Bar':
        pedestrians = pedestrian_df[(pedestrian_df['Sensor_Name'] == selected_source) &
                                    (pedestrian_df['N_Month'] == selected_month)]

        filtered_heatmap = pedestrians.sort_values(by='Year')

        heat = px.histogram(filtered_heatmap, y=filtered_heatmap['Hourly_Counts'],
                            x=filtered_heatmap['Day'], facet_col=filtered_heatmap['Year'],
                            color=filtered_heatmap['Day'],
                            category_orders={
                                "Day": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
                            labels={'Times': 'Hours of The Day',
                                    'Hourly_Counts': 'Hourly Count'})

        for axis in heat.layout:
            if type(heat.layout[axis]) == go.layout.XAxis:
                heat.layout[axis].title.text = ''
        heat.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        heat.update_layout(height=225, margin={'l': 0, 'b': 30, 'r': 0, 't': 30},
                           title='Covid Comparison Barplot',
                           coloraxis_showscale=False, showlegend=False,
                           font=dict(size=8), title_font_color="black"
                           )
        return heat

    # if map is Pedestrian and we have not selected Covid-Bar then plot a heatmap from the filtered data below
    else:
        pedestrians = pedestrian_df[(pedestrian_df['Sensor_Name'] == selected_source) &
                                    (pedestrian_df['Year'] == selected_destination)]
        pedestrians = pedestrians.sort_values(by='Day')

        heat = go.Figure()
        heat.add_trace(go.Heatmap(
            z=pedestrians['Hourly_Counts'],
            x=pedestrians['Time'],
            y=pedestrians['Day'],
            colorscale='Magma'
        ))

        heat.update_layout(height=225, margin={'l': 0, 'b': 0, 'r': 10, 't': 30},
                           title='Hourly Count by Time and Days of Week',
                           xaxis_nticks=12,
                           font=dict(size=10), title_font_color="black",
                           yaxis_title="Weekdays", xaxis_title="Time of Day"
                           )
    return heat

if __name__ == '__main__':
    app.run_server(debug=True)
