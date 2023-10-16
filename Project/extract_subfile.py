import csv

# Open the input CSV file for reading and the output CSV file for writing
with open("agroclimatology.csv", mode="r") as input_file, open("filtered_data.csv", mode="w", newline="") as output_file:
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
                #if 2003 <= value_int <= 2010:
                if 2008 <= value_int <= 2010:   #just to have a faster elaboration of data
                    csv_writer.writerow(row)  # Write the row to the output file

            except ValueError:
                pass  # If the value is not an integer, skip the row



# The filtered rows have been written to "filtered_data.csv"
