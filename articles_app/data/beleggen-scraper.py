import requests
import os
import csv
import pandas as pd
import random as rd
from datetime import datetime


url = "https://www.beleggen.nl/koersen/amx.aspx"

all_headers = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/85.0.564.44']


def clean_dataframe(df_main):

    df_main["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_main["index"] = "AMX"
    df_main.drop("Tijd", axis=1, inplace=True)

    new_labels = {"Fonds": "stock",
             "Koers": "latest",
             "+/-": "abs_delta",
             "%": "abs_perc",
             "Volume": "volume",
             "Open": "open",
             "Hoog": "high",
             "Laag": "low"}

    df_main.rename(columns=new_labels, inplace=True)

    # fixing the dtypes of the columns
    df_main["abs_delta"] = df_main["abs_delta"].str.replace(",", ".").astype("float")
    df_main["abs_perc"] = df_main["abs_perc"].str.replace("%", "").str.replace(",", ".").astype("float")

    # fixing any round off errors
    df_main["latest"] = df_main["latest"].apply(lambda x: round(x, 3))
    df_main["open"] = df_main["open"].apply(lambda x: round(x, 3))
    df_main["high"] = df_main["high"].apply(lambda x: round(x, 3))
    df_main["low"] = df_main["low"].apply(lambda x: round(x, 3))


if __name__ == "__main__":
    header = {'user-agent': rd.choice(all_headers)}

    response = requests.get(url, headers=header)

    # parsing it to a pandas dataframe
    df_stock = pd.read_html(response.text, thousands=".", decimal=",")[0]
    clean_dataframe(df_stock)
    
    # writing it into a csv file
    data_path = r"beleggen_data_AMX.csv"
    if os.path.isfile(data_path):
        df_stock.to_csv(data_path, sep=";", index=False, header=False, mode="a")
    else:
        df_stock.to_csv(data_path, sep=";", index=False, header=True)