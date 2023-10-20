import os.path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Import data
fullpath = r'C:\Users\claud\Documents\GitHub\Python_DSIA\Project\output\filtered_data.csv'
df = pd.read_csv(fullpath)


# Group the DataFrame by the first four characters of the "data" column and calculate the mean for the "TS" column
#new_df = df.groupby(['data']).astype(str).str[:4]
# Group the DataFrame by latitude and longitude
#grouped = new_df.groupby(['latitude', 'longitude'])
# Extract the first 4 characters from the first column and create a new column
df['year'] = df['data'].astype(str).str[:4]
new_df = df.groupby('year')
print(df)
# Group the DataFrame by the new column (first_4_chars) and calculate the mean for another column (e.g., 'YourNumericColumn')
mean_values = []
for column_name in new_df.columns:
    column = df[column_name]
    #Calculate the mean of each column:
    column_mean = column.mean()
    mean_values.append([column_name, column_mean])

#print(len(new_df))  #14: sono 14 anni dal 2004 al 2017
#print(mean_values)



# mean_temp_TS = new_df.groupby('year')['TS'].mean()
# mean_temp_T2MWET = new_df.groupby('year')['T2MWET'].mean()
# mean_temp_T2M = new_df.groupby('year')['T2M'].mean()
# mean_humidity_QV2M = new_df.groupby('year')['QV2M'].mean()
# mean_pressure = new_df.groupby('year')['PS'].mean()
# Print the result
# print(f'mean_temp_TS: ', len(mean_temp_TS))
# print(f'mean_humidity', len(mean_humidity_QV2M))

# Create a histogram
# plt.hist(mean_temp_TS, bins=5, color='skyblue', edgecolor='black')

# # Customize the plot
# plt.xlabel('Temperature')
# plt.ylabel('Occurrency')
# plt.title('Mean temperature along the years')

# # Display the histogram
# plt.show()




# # Adjust layout and display
# plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# plt.show()


# # Create a figure and subplots
# fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# # Create histograms on each subplot
# axes[0].hist(mean_values(), bins=20, color='blue', alpha=0.7)
# axes[0].set_title('TS')

# axes[1].hist(mean_values(), bins=20, color='green', alpha=0.7)
# axes[1].set_title('T2MWET')

# axes[2].hist(mean_values[], bins=20, color='red', alpha=0.7)
# axes[2].set_title('T2M')

# # Set common labels for all subplots
# for ax in axes:
#     ax.set_xlabel('X-axis Label')
#     ax.set_ylabel('Frequency')

# # Add a title to the entire figure
# fig.suptitle('Subplots with Histograms')

# # Display the figure
# plt.show()