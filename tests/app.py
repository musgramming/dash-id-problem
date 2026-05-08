from dash import Dash, html
import dash
from flask import Flask 
import dash_bootstrap_components as dbc

app  = Dash(
    __name__, 
    pages_folder= "pages", 
    use_pages = True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


app.layout = html.Div([
    dash.page_container 
])


if __name__ == "__main__":
    app.run(debug = True)