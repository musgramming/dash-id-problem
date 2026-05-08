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
    print("="*50)
    print(f"Số lượng trang tìm thấy: {len(dash.page_registry)}")
    for page_id, page_info in dash.page_registry.items():
        print(f"--- Page: {page_id} ---")
        print(f"  + Path: {page_info['path']}")
        print(f"  + Module: {page_info['module']}")
        print(f"  + File: {page_info['relative_path']}")
    print("="*50)
    app.run(debug = True)