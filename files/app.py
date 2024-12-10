from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import webbrowser
from threading import Timer

# Load and validate the dataset
try:
    file_path = "/Users/joshuabrooks/applehealth-1/files/Book5.xlsx"  # Update this to your file path if different
    data = pd.read_excel(file_path, sheet_name='Query')
    data = data.rename(columns={'Attribute:type': 'Type', 'Attribute:creationDate': 'Timestamp', 'Attribute:value': 'Value'})
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
except Exception as e:
    print(f"Error loading data: {e}")
    data = pd.DataFrame(columns=['Type', 'Timestamp', 'Value'])  # Empty DataFrame fallback

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # Default filters
    selected_type = data['Type'].unique()[0] if not data.empty else "None"
    start_date = data['Timestamp'].min().date() if not data.empty else pd.Timestamp.today().date()
    end_date = data['Timestamp'].max().date() if not data.empty else pd.Timestamp.today().date()
    
    # Handle form submission
    if request.method == "POST":
        selected_type = request.form.get("type")
        start_date = pd.to_datetime(request.form.get("start_date"))
        end_date = pd.to_datetime(request.form.get("end_date"))
    
    # Filter data
    filtered_data = data[
        (data['Type'] == selected_type) &
        (data['Timestamp'] >= pd.Timestamp(start_date)) &
        (data['Timestamp'] <= pd.Timestamp(end_date))
    ]

    # Calculate statistics
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
                           types=data['Type'].unique() if not data.empty else [],
                           selected_type=selected_type,
                           start_date=start_date,
                           end_date=end_date,
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
