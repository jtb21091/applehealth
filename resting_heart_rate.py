import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import statistics
from datetime import datetime

def calculate_and_plot_resting_hr(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    resting_hr_values = []
    timestamps = []

    for record in root.findall('Record'):
        if record.attrib.get('type') == 'HKQuantityTypeIdentifierRestingHeartRate':
            value = float(record.attrib.get('value'))
            date_str = record.attrib.get('startDate')
            try:
                # Keep full datetime for more precise plotting
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
            except Exception as e:
                print(f"Skipping record with bad date: {date_str}")
                continue

            resting_hr_values.append(value)
            timestamps.append(date)

    if resting_hr_values:
        avg_hr = statistics.mean(resting_hr_values)
        median_hr = statistics.median(resting_hr_values)
        std_dev = statistics.stdev(resting_hr_values)

        upper_bound = avg_hr + 2 * std_dev
        lower_bound = avg_hr - 2 * std_dev

        # Print statistics
        print(f"Average Resting HR: {avg_hr:.2f} bpm")
        print(f"Median Resting HR: {median_hr:.2f} bpm")
        print(f"Standard Deviation: {std_dev:.2f} bpm")

        # Plotting
        plt.figure(figsize=(14, 6))
        plt.scatter(timestamps, resting_hr_values, label='Resting HR', color='blue', alpha=0.7)
        plt.axhline(avg_hr, color='green', linestyle='--', label=f'Average: {avg_hr:.2f} bpm')
        plt.axhline(median_hr, color='orange', linestyle='--', label=f'Median: {median_hr:.2f} bpm')
        plt.axhline(upper_bound, color='red', linestyle=':', label=f'+2 SD: {upper_bound:.2f} bpm')
        plt.axhline(lower_bound, color='red', linestyle=':', label=f'-2 SD: {lower_bound:.2f} bpm')

        plt.title('Resting Heart Rate Over Time (Scatter)')
        plt.xlabel('Date')
        plt.ylabel('Heart Rate (bpm)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        plt.savefig("resting_hr_scatter_plot.png")
        plt.show()

    else:
        print("No resting heart rate data found.")

# Run it
calculate_and_plot_resting_hr('/Users/joshuabrooks/Downloads/apple_health_export/export.xml')
