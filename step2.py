from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import webbrowser
from threading import Timer

# Load and validate the dataset
try:
    file_path = "/Users/joshuabrooks/applehealth-2/health_data_records.csv"  # Update if needed

    # Load CSV with forced data types to prevent errors
    data = pd.read_csv(file_path, dtype=str, low_memory=False)

    # Print column names to verify structure
    print("Columns in CSV:", data.columns)

    # Rename columns if necessary
    if "creationDate" in data.columns:
        data = data.rename(columns={'creationDate': 'Timestamp'})

    # Check if Timestamp column exists after renaming
    if 'Timestamp' not in data.columns:
        raise ValueError("Timestamp column not found in CSV! Check column names.")

    # Convert Timestamp to datetime & remove timezone
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
    if data['Timestamp'].dt.tz is not None:  # If timezone exists, make it naive
        data['Timestamp'] = data['Timestamp'].dt.tz_localize(None)

    # Ensure Value column is numeric
    if 'value' in data.columns:
        data = data.rename(columns={'value': 'Value'})  # Standardize column name
        data['Value'] = pd.to_numeric(data['Value'], errors='coerce')

    # Drop rows where Timestamp is NaT (invalid date)
    data = data.dropna(subset=['Timestamp'])

except Exception as e:
    print(f"Error loading data: {e}")
    data = pd.DataFrame(columns=['type', 'Timestamp', 'Value'])  # Empty DataFrame fallback

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # Handle case where dataset is empty
    if data.empty:
        return render_template("index.html",
                               types=[],
                               selected_type="None",
                               start_date="",
                               end_date="",
                               graph_html="<p>No data available.</p>",
                               mean_value=0,
                               upper_limit=0,
                               lower_limit=0)

    # Default filters
    selected_type = request.form.get("type", data['type'].unique()[0])
    start_date = request.form.get("start_date", data['Timestamp'].min().date())
    end_date = request.form.get("end_date", data['Timestamp'].max().date())

    # Convert start and end date, ensuring timezone consistency
    start_date = pd.to_datetime(start_date).tz_localize(None)
    end_date = pd.to_datetime(end_date).tz_localize(None)

    # Filter data
    filtered_data = data[
        (data['type'] == selected_type) &
        (data['Timestamp'] >= start_date) &
        (data['Timestamp'] <= end_date)
    ]

    # Calculate statistics and generate graph
    if not filtered_data.empty:
        mean_value = filtered_data['Value'].mean()
        std_dev = filtered_data['Value'].std()
        upper_limit = mean_value + 2 * std_dev
        lower_limit = mean_value - 2 * std_dev

        # Generate Plotly graph
        fig = px.line(filtered_data, x='Timestamp', y='Value', title=f"{selected_type} Over Time")
        fig.add_scatter(x=filtered_data['Timestamp'], y=[mean_value] * len(filtered_data), mode='lines',
                        name='Mean', line=dict(dash='dash', color='green'))
        fig.add_scatter(x=filtered_data['Timestamp'], y=[upper_limit] * len(filtered_data), mode='lines',
                        name='Upper 2 Std Dev', line=dict(dash='dot', color='red'))
        fig.add_scatter(x=filtered_data['Timestamp'], y=[lower_limit] * len(filtered_data), mode='lines',
                        name='Lower 2 Std Dev', line=dict(dash='dot', color='blue'))
        graph_html = pio.to_html(fig, full_html=False)
    else:
        mean_value, std_dev, upper_limit, lower_limit = 0, 0, 0, 0
        graph_html = "<p>No data available for the selected filters.</p>"

    # Render the HTML template with data
    return render_template("index.html",
                           types=data['type'].unique(),
                           selected_type=selected_type,
                           start_date=start_date.date(),
                           end_date=end_date.date(),
                           graph_html=graph_html,
                           mean_value=mean_value,
                           upper_limit=upper_limit,
                           lower_limit=lower_limit)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Open the browser automatically
    Timer(1, open_browser).start()
    app.run(debug=True)
