# Mục đích của trang: Kiểm tra tính đúng đắn của phương thức ALL bằng cách cho bạn nhập số lượng ô, rồi tính tổng của chúng

from dash import html, dcc, Input, Output, State, callback, register_page
import dash_bootstrap_components as dbc
from utils.direction.direction_plain import PageDirection 
from utils.direction import pds, pdp

register_page(
    __name__, 
    path="/sum"
)

pg = pds.assign_page()

layout = dbc.Container([
    html.H3("Test Tính năng ALL - Tính Tổng Động", className="text-center my-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("＋ Thêm ô", id=pg.assign_id("btn-add"), color="primary"),
                dbc.Button("－ Bớt ô", id=pg.assign_id("btn-remove"), color="danger"),
            ]),
            html.Hr(),
            # Nơi chứa các ô Input sinh ra động
            html.Div(
                [dbc.Input(id=pg.assign_id("num-input", is_dynamic=True), type="number", value=0, className="mb-2")],
                id=pg.assign_id("input-container")
            )
        ], width=6),
        
        dbc.Col([
            html.Div([
                html.H4("Tổng cộng:"),
                html.H1("0", id=pg.assign_id("total-display"), className="text-success")
            ], className="p-4 border rounded text-center")
        ], width=6)
    ])
], fluid=True)

# 1. Callback Thêm/Bớt ô
@callback(
    Output(pg.use_id("input-container"), "children"),
    Input(pg.use_id("btn-add"), "n_clicks"),
    Input(pg.use_id("btn-remove"), "n_clicks"),
    State(pg.use_id("input-container"), "children"),
    prevent_initial_call=True
)
def manage_inputs(add_clicks, remove_clicks, current_children):
    from dash import ctx
    if not ctx.triggered:
        return current_children
    
    triggered_id = ctx.triggered_id 
    page = pds.use_page() 

    if triggered_id == page.use_id("btn-add"):
        new_id = page.next_index("num-input")
        new_input = dbc.Input(id=new_id, type="number", value=0, className="mb-2")
        current_children.append(new_input)
        
    elif triggered_id == page.use_id("btn-remove"):
        if len(current_children) > 1:
            page.reduce_index("num-input")
            current_children.pop()
            
    return current_children




# 2. Callback Tính Tổng dùng ALL
@callback(
    Output(pg.use_id("total-display"), "children"),
    Input(pg.all("num-input"), "value") # ĐÂY LÀ PHÉP ALL "THẦN THÁNH" CỦA BẠN
)
def update_total(values):
    if not values:
        return 0
    # Dash trả về list các giá trị từ các ô có ID match với ALL
    total = sum(float(v) if v is not None else 0 for v in values)
    return f"{total:,}"