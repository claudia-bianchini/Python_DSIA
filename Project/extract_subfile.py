import csv
import os

# Define the path to the input CSV file
input_file_path = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\input\agroclimatology.csv'

# Define the path to the output folder
output_folder = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Define the output file path within the output folder
output_file_path = os.path.join(output_folder, "filtered_data.csv")

# Open the input CSV file for reading and the output CSV file for writing
with open(input_file_path, mode="r") as input_file, open(output_file_path, mode="w", newline="") as output_file:
    # Create CSV readers and writers
    csv_reader = csv.reader(input_file)
    csv_writer = csv.writer(output_file)

    # Write the header to the output file
    header = next(csv_reader)
    csv_writer.writerow(header)

    # Iterate through the rows and filter based on the conditions
    for row in csv_reader:
        if len(row) >= 1:
            value = row[0][:4]  # Get the first 4 characters of "Column1"
            try:
                value_int = int(value)  # Try to convert the value to an integer
                if 2013 <= value_int <= 2017:   # Filter based on the specified range
                    csv_writer.writerow(row)  # Write the row to the output file
            except ValueError:
                pass  # If the value is not an integer, skip the row

# The filtered rows have been written to "filtered_data.csv" in the "output" folder
