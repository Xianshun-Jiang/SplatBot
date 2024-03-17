import csv
import json

name = "all"

# Open the CSV file for reading
with open(name+'.csv', 'r') as csv_file:
    # Create a CSV reader
    csv_reader = csv.DictReader(csv_file)
    
    # Convert CSV to dictionary
    data = list(csv_reader)

# Convert the dictionary to JSON and save to a file
with open(name + '.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)