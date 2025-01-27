from dash import Dash, Input, Output, html
from dash_pydantic_form import ModelForm
from pydantic import BaseModel

app = Dash(__name__)

class MyModel(BaseModel):
    name: str
    age: int

AIO_ID = "my-form"
FORM_ID = "form"

form = ModelForm(
    item=MyModel,
    aio_id=AIO_ID,
    form_id=FORM_ID,
    store_progress="session",
)

@app.callback(
    Output(ModelForm.ids.main(AIO_ID, FORM_ID), "data"),
    Input("update-button", "n_clicks"),
)
def update_form(n_clicks):
    if n_clicks:
        new_data = {"name": "John Doe", "age": 30}
        return new_data
    return None

app.layout = html.Div(
    [
        form,
        html.Button("Update Form", id="update-button"),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)