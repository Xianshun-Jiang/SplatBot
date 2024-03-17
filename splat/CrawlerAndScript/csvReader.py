import csv

# Open the CSV file in read mode
with open('./weapons_data.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)

