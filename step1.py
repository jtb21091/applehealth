import xml.etree.ElementTree as ET
import csv

# Define input and output file paths
xml_file = "export.xml"  # Replace with your actual XML file name
csv_file = "health_data_records.csv"

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Open CSV file for writing
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Define header row based on attributes in the Record element
    header = ["type", "sourceName", "sourceVersion", "unit", "creationDate", 
              "startDate", "endDate", "value", "device", "metadataEntry"]
    writer.writerow(header)

    # Extract each Record and write to CSV
    for record in root.findall("Record"):
        # Extract attributes
        row = [
            record.get("type"),
            record.get("sourceName"),
            record.get("sourceVersion"),
            record.get("unit"),
            record.get("creationDate"),
            record.get("startDate"),
            record.get("endDate"),
            record.get("value"),
            record.get("device"),
            record.get("metadataEntry")
        ]
        writer.writerow(row)

print(f"Conversion complete! CSV file saved as {csv_file}")
