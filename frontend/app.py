import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

from dash.dependencies import Input, Output, State

# from dbconnector import db_connect, EtfCategory
# from sqlalchemy.orm import sessionmaker


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

#engine = db_connect()
#Session = sessionmaker(engine)
#session = Session()
#categories = session.query(EtfCategory).all()
#session.close()

categories = ['Sector', 'Country', 'Region', 'Asset Class', 'Strategy', 'Currency', 'Bond Type', 'Commodity Class', 'Bond Maturity', 'Rating']
test_data_dropdown = [(1, 'A'), (2, 'B'), (3, 'C')]
test_data_table = [{'id': 'column1', 'name': 'Column 1'}, {'id': 'column2', 'name': 'Column 2'}, {'id': 'column3', 'name': 'Column 3'}]
test_data_pie_chart = {'A' : 10, 'B' : 10, 'C' : 10}


def create_dropdown(dropdown_id, dropdown_data, width):
    dropdown = html.Div([
        dcc.Dropdown(
            id=dropdown_id + " Dropdown",
            options=[{'value': cat_id, 'label': cat_name} for cat_id, cat_name in dropdown_data],
            multi=True,
            clearable=True,
            placeholder=dropdown_id,
            searchable=True
        ),
    ], style={'width': width, 'display': 'inline-block', 'padding': 10})

    return dropdown


def create_button(button_id):
    button = html.Div([
        dbc.Button(
            button_id,
            id = button_id + " Button",
            n_clicks = 0)
    ], style={'display': 'inline-block', 'padding': 10,})

    return button


def create_table(table_id, table_data, width):
    table = html.Div([
        dash_table.DataTable(
            id=table_id + " Table",
            columns=table_data,
        )
    ], style={'width': width, 'display': 'inline-block', 'padding': 10})

    return table


def create_pie_chart(pie_chart_id, pie_chart_data, width):
    data_keys = list(pie_chart_data.keys())
    data_values = []

    for key in data_keys:
        data_values.append(pie_chart_data.get(key, 0.0))

    pie_chart = html.Div([
        dcc.Graph(
            id=pie_chart_id + " Pie Chart",
            figure=px.pie(
                names=data_keys,
                values=data_values,
            )
        )
    ], style={'width': width, 'display': 'inline-block', 'padding': 10})

    return pie_chart


input_divs = []
for category in categories:
    input_divs.append(create_dropdown(category, test_data_dropdown, '20%'))
input_divs.append(html.Center(create_button('Optimize')))

output_divs = []
output_divs.append(create_table('Optimization', test_data_table, '100%'))
output_divs.append(html.Center(create_pie_chart('Optimization', test_data_pie_chart, '33.33%')))

divs = html.Div([html.Div(input_divs, style={'width': '100%', 'display': 'inline-block'}), html.Div(output_divs, style={'width': '100%', 'display': 'inline-block'})])

app.layout = html.Div(divs, style={'width': '97.5%', 'display': 'inline-block', 'margin-top': "30px", 'margin-bottom': "30px", 'margin-left': "30px", 'margin-right': "30px"})


@app.callback(
    Output(component_id='Optimization Table', component_property='data'),
    [Input(component_id='Optimize Button', component_property='n_clicks')],
    state = [State(component_id=category + ' Dropdown' ,component_property='value') for category in categories]
)

def update_table(num_clicks, sector, country, region, asset_class, strategy, currency, bond_type, commodity_class, bond_maturity, rating):
    # TODO: Update table with optimized values
    return None


@app.callback(
    Output(component_id='Optimization Pie Chart', component_property='figure'),
    [Input(component_id='Optimize Button', component_property='n_clicks')],
    state = [State(component_id=category + ' Dropdown' ,component_property='value') for category in categories]
)

def update_graph(num_clicks, sector, country, region, asset_class, strategy, currency, bond_type, commodity_class, bond_maturity, rating):
    # TODO: Update graph with optimized values
    if num_clicks > 0:
        figure = px.pie(
                    values=[10, 10, 10, 10],
                    names=['A', 'B', 'C', 'D']
                )
        return figure
    else:
        figure = px.pie(
                    values=[10, 10, 10],
                    names=['A', 'B', 'C']
                )
        return figure

if __name__ == '__main__':
    app.run_server(debug=True)
