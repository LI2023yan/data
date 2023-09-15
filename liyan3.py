import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

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
fig = px.pie(data, names=labels, values=sizes, title="Genre Distribution")

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

# Define the app layout
app.layout = html.Div(
    [
        # Title
        html.H1("Top 20 Animation Movies", style={"textAlign": "center"}),
        # Pie Chart (fig1)
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig2),
        dcc.Graph(figure=fig3),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8068)
