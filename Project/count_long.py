import csv

# Open the CSV file for reading
with open("agroclimatology.csv", mode="r") as file:
    # Create a CSV reader
    csv_reader = csv.DictReader(file)
    
    # Skip the header row if it exists
    next(csv_reader, None)

    # Initialize lists to store latitude and longitude values
    latitudes = []
    longitudes = []

    # Create an empty set to store unique values
    unique_years = set()
    first_eight = 0
    spec_day = []
    i = 0
    # Iterate through the rows and extract latitude and longitude
    for row in csv_reader:
        latitudes.append(float(row["latitude"]))
        longitudes.append(float(row["longitude"]))
        if len(row) > 0:
            value = row['data'][:4]  # Get the first 4 characters of the first column
            unique_years.add(value)
            if row['data'] == '20090325':     #how many data per each date
                spec_day.append([row['latitude'],row['longitude']])
                
                first_eight +=1

    
    latitudes = set(latitudes)
    longitudes = set(longitudes)


        
# Now you have 

# Now you have two lists containing latitude and longitude
#and a set containing unique values based on the first 4 characters of the first column

print("Latitudes:", len(latitudes))
print("Longitudes:", len(longitudes))
print("Unique Values:", sorted(unique_years))
print('Number of samples per 25/03/2009:', first_eight)
#print(len(spec_day))

#Now I want to extract only unique values that are present in spec_day list:
unique_spec_day = []
url_set = set()

for item in spec_day:
    item_tuple = tuple(item)
    if item_tuple not in url_set:
        url_set.add(item_tuple)
        unique_spec_day.append(item)
    else:
        pass

print(unique_spec_day)
print(f'We have {len(unique_spec_day)} different postition per measurment per day')


