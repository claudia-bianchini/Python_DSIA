import pandas as pd

def rinomina_colonne(dataframe, dizionario_rinomina):
    """
    Rinomina le colonne di un DataFrame utilizzando un dizionario di mappatura.

    Args:
        dataframe (pd.DataFrame): Il DataFrame da rinominare.
        dizionario_rinomina (dict): Un dizionario che mappa i nomi delle colonne originali ai nuovi nomi.

    Returns:
        pd.DataFrame: Il DataFrame con le colonne rinominate.
    """
    return dataframe.rename(columns=dizionario_rinomina)

# Esempio d'uso:
data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)

nuovi_nomi_colonne = {'A': 'Colonna1', 'B': 'Colonna2'}
df_rinominato = rinomina_colonne(df, nuovi_nomi_colonne)

print(df_rinominato)