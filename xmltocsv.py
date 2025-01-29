import xml.etree.ElementTree as ET
import pandas as pd

def xml_to_csv(xml_file, csv_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = []
    for elem in root.findall(".//"):
        row = {}
        for subelem in elem:
            row[subelem.tag] = subelem.text
        if row:
            data.append(row)

    if data:
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)
        print(f"CSV file saved successfully as: {csv_file}")
    else:
        print("No data found in XML file.")

# Replace with your file paths
xml_file = "/Users/joshuabrooks/Desktop/apple_health_export 2/export.xml"
csv_file = "output.csv"     # Change this to desired output file

xml_to_csv(xml_file, csv_file)
