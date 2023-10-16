import pandas as pd

# Read the first CSV file into a DataFrame
df_data = pd.read_csv("agroclimatology.csv")

# Read the second CSV file into another DataFrame
df_soja = pd.read_csv("productividade_soja.csv")


# Iterate through the rows and filter based on the conditions
mena_humidity = []
    for row in df_data:
        if len(row) >= 1:
            value = row[0][:4]  # Get the first 4 characters of "Column1": we select the year

            mean_humidity[value] = mean_humidity[value] + row['GWETPROF']/2
            
            mean_humidity[value] = [value, codigo_ibge, mean]


soeil_mean = df_data['GWETPROF'].mean



#grafico dell'umiditò delle radici media nell'anno associata alla produzione di soja
#anni 2004/2017

