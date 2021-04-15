import dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_bootstrap_components as dbc
# from sqlalchemy.orm import sessionmaker

# from dbconnector import db_connect, EtfCategory

app = dash.Dash(__name__)

#engine = db_connect()
#Session = sessionmaker(engine)
#session = Session()
#categories = session.query(EtfCategory).all()
#session.close()

categories = [(1, 'USA', ''), (2, 'Germany', ''), (3, 'China', '')]

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='categories-filter',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            #persistence=True?
            placeholder='Select categories for your portfolio',
            searchable=True
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='categories-filter2',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            #persistence=True?
            placeholder='Select categories for your portfolio',
            searchable=True
        )
    ], style={'width': '30%', 'display': 'inline-block', 'padding': 10}),
])

if __name__ == '__main__':
    app.run_server(debug=True)
