# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Output, Input, State


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button("Click me", id="open"),
                html.Div("...", id="text"),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Header")),
                        dbc.ModalBody("This is the content of the modal"),
                        dbc.ModalFooter([
                            dbc.Button(
                                "Save", id="accept", className="ms-auto", n_clicks=0
                            ),
                            dbc.Button(
                                "Close", id="close", className="ms-auto", n_clicks=0
                            ),
                        ]),
                    ],
                    id="modal",
                    is_open=False,
                ),
            ]),
        ]),
    ]),
])



@app.callback(
    Output("modal", "is_open"),
    Output("text", "children"),

    Input("open", "n_clicks"),
    Input("close", "n_clicks"),
    Input("accept", "n_clicks"),

    State("modal", "is_open"),
)
def toggle_modal(n1, n2, accept_n_clicks, is_open):
    ctx = dash.callback_context

    first, *_ = ctx.triggered
    if first["prop_id"] == "accept.n_clicks":
        # User clicked "Save"
        ...
        return False, "User clicked save" # close the modal
    elif first["prop_id"] == "close.n_clicks":
        # User clicked "Cancel"
        ...
        return False, "User clicked cancel"
    elif first["prop_id"] == "open.n_clicks":
        # User wants to open dialog
        ...
        return True, "dialog open"


if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_hot_reload=False)
