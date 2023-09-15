import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash.dash import no_update
import urllib.parse
import io
import base64

app = dash.Dash(__name__)

data_url = "https://raw.githubusercontent.com/LI2023yan/data/main/Top%2050%20Animation%20Movies%20and%20TV%20Shows.csv"
df = pd.read_csv(data_url)

server = app.server

# DATA CLEANING
data = df.dropna().copy()

data["Minutes"] = data["Minutes"].str.split(" ").str[0]
data.Minutes = data.Minutes.astype(int)

data["Votes"] = data["Votes"].str.replace(",", "")
data.Votes = data.Votes.astype(int)

# Calculate genre distribution
genre_counts = data["genre"].value_counts()
labels = genre_counts.index
sizes = genre_counts.values


# Create a Plotly Express pie chart
def update_pie_chart(selected_genres):
    filtered_data = data[data["genre"].isin(selected_genres)]
    genre_counts_filtered = filtered_data["genre"].value_counts()
    labels_filtered = genre_counts_filtered.index
    sizes_filtered = genre_counts_filtered.values
    fig = px.pie(
        filtered_data,
        names=labels_filtered,
        values=sizes_filtered,
        title="Genre Distribution",
    )
    return fig


# Calculate the order for the bar chart
order_min = data.groupby("Name").mean().sort_values("Minutes", ascending=False).index

# Create a Plotly Express bar chart for the movie/TV show with the highest Minutes
fig2 = px.bar(
    data,
    y="Name",
    x="Minutes",
    title="Movie/TV Show with highest Minutes",
    category_orders={"Name": order_min},
)

# Create a Plotly Express scatter plot for Rating versus Votes
fig3 = px.scatter(
    data,
    x="Rating",
    y="Votes",
    color_continuous_scale=px.colors.sequential.Plasma,
    template="plotly_dark",
    title="<b>Rating Versus Votes",
)

# Define the app layout with tabs
app.layout = html.Div(
    [
        # Title
        html.H1("Top 20 Animation Movies", style={"textAlign": "center"}),
        # Tabs
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Genre Distribution",
                    children=[
                        html.Div(
                            [
                                html.Label("Select Genres:"),
                                dcc.Checklist(
                                    id="genre-checklist",
                                    options=[
                                        {"label": genre, "value": genre}
                                        for genre in labels
                                    ],
                                    value=labels,  # Default: All genres selected
                                    inline=True,  # Display checklist items horizontally
                                ),
                                dcc.Graph(id="genre-pie-chart"),
                                # Download button for CSV
                                html.Div(
                                    [
                                        dcc.Download(id="download-csv"),
                                        html.Button(
                                            "Download CSV",
                                            id="btn-download",
                                            n_clicks=0,
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                ),
                dcc.Tab(label="Highest Minutes", children=[dcc.Graph(figure=fig2)]),
                dcc.Tab(label="Rating vs Votes", children=[dcc.Graph(figure=fig3)]),
            ]
        ),
    ]
)


# Callback to update the pie chart based on checklist selections
@app.callback(
    Output("genre-pie-chart", "figure"),
    Input("genre-checklist", "value"),
)
def update_pie(selected_genres):
    fig = update_pie_chart(selected_genres)
    return fig


# Callback to handle the download button click
@app.callback(
    Output("download-csv", "data"),
    Input("btn-download", "n_clicks"),
)
def download_csv(n_clicks):
    if not n_clicks:
        raise PreventUpdate

    selected_data = data[data["genre"].isin(labels)]
    csv_string = selected_data.to_csv(index=False, encoding="utf-8")

    # Create a CSV file in memory
    csv_bytes = io.BytesIO(csv_string.encode("utf-8"))

    # Encode the CSV file as base64
    csv_base64 = base64.b64encode(csv_bytes.read()).decode("utf-8")

    return dict(content=csv_base64, filename="selected_data.csv")


if __name__ == "__main__":
    app.run_server(debug=True, port=8068)
