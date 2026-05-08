from dash import register_page, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc 
from utils.models.triangle import solve_triangle 

register_page(
    __name__, 
    path="/triangle-test",
    name="Triangle Geometry Test"
)

layout = dbc.Container([
    html.H3("Kiểm tra Hình học Tam giác", className="text-center my-4"),
    
    dbc.Row([
        # Cột nhập tọa độ
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Nhập tọa độ các đỉnh"),
                dbc.CardBody([
                    dbc.Label("Đỉnh A (x1, y1)"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Input(
                                id="t-x1", 
                                type="number", 
                                placeholder="x1"
                            )
                        ),
                        dbc.Col(
                            dbc.Input(
                                id="t-y1", 
                                type="number", 
                                placeholder="y1"
                            )
                        ),
                    ], className="mb-2"),
                    
                    dbc.Label("Đỉnh B (x2, y2)"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Input(
                                id="t-x2", 
                                type="number", 
                                placeholder="x2"
                            )
                        ),
                        dbc.Col(
                            dbc.Input(
                                id="t-y2", 
                                type="number", 
                                placeholder="y2"
                            )
                        ),
                    ], className="mb-2"),
                    
                    dbc.Label("Đỉnh C (x3, y3)"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Input(
                                id="t-x3", 
                                type="number", 
                                placeholder="x3"
                            )
                        ),
                        dbc.Col(
                            dbc.Input(
                                id="t-y3", 
                                type="number", 
                                placeholder="y3"
                            )
                        ),
                    ], className="mb-3"),
                    
                    dbc.Button(
                        "Giải tam giác", 
                        id="t-btn-solve", 
                        color="success", 
                        className="w-100"
                    )
                ])
            ])
        ], width=4),
        
        dbc.Col([
            html.Div(id="t-output-container")
        ], width=8)
    ])
], fluid=True)

@callback(
    Output("t-output-container", "children"),
    Input("t-btn-solve", "n_clicks"),
    [State("t-x1", "value"), State("t-y1", "value"),
     State("t-x2", "value"), State("t-y2", "value"),
     State("t-x3", "value"), State("t-y3", "value")],
    prevent_initial_call=True
)
def update_result(n_clicks, x1, y1, x2, y2, x3, y3):
    result = solve_triangle(x1, y1, x2, y2, x3, y3)
    
    if not result["Tồn tại"]:
        return dbc.Alert(f"Lỗi: {result['Lỗi']}", color="danger", className="mt-3")
    
    data_dict = result["Kết quả"]
    table_data = [
        {"Thông số": k, "Giá trị": str(v)} for k, v in data_dict.items()
    ]
    
    return html.Div([
        html.H5("Kết quả phân tích:", className="mb-3"),
        dash_table.DataTable(
            data=table_data,
            columns=[
                {
                    "name": "Thông số", 
                    "id": "Thông số"
                }, 
                {
                    "name": "Giá trị", 
                    "id": "Giá trị"
                }
            ],
            style_cell={
                'textAlign': 'left', 
                'padding': '12px'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {
                        'row_index': 'odd'
                    },
                    'backgroundColor': '#f9f9f9'
                }
            ],
            style_table={
                'border': '1px solid #dee2e6'
            }
        )
    ], className="mt-3")