import pandas as pd
import random as rd
import csv
import requests
import os
import re

from datetime import datetime
from bs4 import BeautifulSoup

data_file = r"AMX_prices.csv"
AMX_components_url = "https://solutions.vwdservices.com/customers/nos.nl/quotecube/Composition/List/AMX?_=1599474611342"
AMX_index_url = "https://solutions.vwdservices.com/customers/nos.nl/quotecube/OverView/Market/AMX?_=1600101564446"
AMX_index_ohlc_url = "https://teletekst-data.nos.nl/json/503-2"



all_headers = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/85.0.564.44']


def get_components_dataframe(response):
    """Gets all components of the AMX of the NOS.nl

    Args:
        response requests.models.Response: The response from the webpage call when a request is being made

    Returns:
        pandas.DataFrame: The dataframe with all the uncleaned component data from the AMX
    """
    df_all = pd.read_html(response.text, decimal=',', thousands='.')

    df_stats = df_all[0].copy(deep=True)
    df_ohlc = df_all[1].copy(deep=True)

    df_main = df_stats.join(df_ohlc)
    return df_main


def clean_components(df_main):
    """Clean all the columns in the dataframe 

    Args:
        df_main pandas.DataFrame: The uncleaned dataframe with all components of the AMX
    """
    df_main["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_main["index"] = "AMX"
    df_main.drop("Uur", axis=1, inplace=True)
    df_main.drop("Koers", axis=1, inplace=True)

    new_labels = {"Naam": "stock",
             "+/-": "abs_delta",
             "+/- %": "abs_perc",
             "Volume": "volume",
             "Open": "open",
             "Hoog": "high",
             "Laag": "low",
             "Slot": "close"}

    df_main.rename(columns=new_labels, inplace=True)

    # fixing the dtypes of the columns
    df_main["abs_delta"] = df_main["abs_delta"].str.replace(",", ".").astype("float")
    df_main["abs_perc"] = df_main["abs_perc"].str.replace("%", "").str.replace(",", ".").astype("float")

    # fixing any round off errors
    df_main["close"] = df_main["close"].apply(lambda x: round(x, 3))
    df_main["open"] = df_main["open"].apply(lambda x: round(x, 3))
    df_main["high"] = df_main["high"].apply(lambda x: round(x, 3))
    df_main["low"] = df_main["low"].apply(lambda x: round(x, 3))


def get_index_ohlc_info(response):
    """Gets all the info from teletekst.nl about the ohlc of the AMX,
    because the website doesn't supply all the ohlc data.

    Args:
        response requests.models.Response: The response from the webpage call when a request is being made

    Returns:
        tuple: A tuple with all the information about the ohlc of the AMX
    """
    content = response.text
    # convert to beautifulSoup
    soup = BeautifulSoup(content, 'lxml')
    # filter all the html tags out of it
    all_text = soup.text
    # find all the text between AMX and ASCX
    filter1 = str(re.findall("AMX.*?ASCX", all_text)[0])
    # filter out all the extra spaces
    filter2 = re.sub('\s+', ' ', filter1)
    # Split the remaining text on 
    filter3 = filter2.split("\\n")

    index_open = filter3[1].split(" ")[2].replace(",", ".")
    index_high = filter3[2].split(" ")[2].replace(",", ".")
    index_low = filter3[3].split(" ")[2].replace(",", ".")
    index_close_yesterday = filter3[0].split(" ")[1].replace(",", ".")

    return float(index_open), float(index_high), float(index_low), float(index_close_yesterday)


def get_index_info(response):
    """Get all the basic info about the index itself.

    Args:
        response requests.models.Response: The response from the webpage call when a request is being made

    Returns:
        pandas.DataFrame: A Dataframe with all the info about the index' standings
    """
    content = response.text
    # convert to beautifulSoup
    soup = BeautifulSoup(content, 'lxml')
    # filter all the html tags out of it
    all_text = soup.text
    # find all the text between AMX and ASCX
    filter1 = str(re.findall("AMX.*?ASCX", all_text)[0])
    # filter out all the extra spaces
    filter2 = re.sub('\s+', ' ', filter1)
    # filter the remaining text on '\\n'
    filter3 = filter2.split("\\n")

    index_abs_perc = 0.0
    if " - " in filter3[0]:
        # filter the minus sign ( - ) out of the first array
        filter4 = filter3[0].split(" - ")
        index_abs_perc = float(filter4[1].replace("%", "").replace(",", ".")) * -1.0
    else:
        filter4 = filter3[0].split(" + ")
        index_abs_perc = float(filter4[1].replace("%", "").replace(",", "."))

    day_diff = filter4[0].split(" ")
    
    # get the index name
    index_name = day_diff[0]
    index_close = day_diff[2].replace(",", ".")
    index_abs_delta = round(float(index_close) - float(day_diff[1].replace(",", ".")), 2)

    index_open = filter3[1].split(" ")[2].replace(",", ".")
    index_high = filter3[2].split(" ")[2].replace(",", ".")
    index_low = filter3[3].split(" ")[2].replace(",", ".")

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df_index = pd.DataFrame([index_name, index_abs_delta, index_abs_perc, 0, index_open, index_high, index_low, index_close, current_date, "AMX"])
    return df_index


def write_to_csv(csv_path, df):
    """Checks if a csv file already exists and writes the dataframe to a csv-file.

    Args:
        csv_path String: The file-path to the csv-file
        df pandas.DataFrame: The dataframe that has to be written into the csv-file
    """
    if os.path.isfile(csv_path):
        df.to_csv(csv_path, sep=";", index=False, header=False, mode="a")
    else:
        df.to_csv(csv_path, sep=";", index=False, header=True)


if __name__ == "__main__":
    header = {'user-agent': rd.choice(all_headers)}

    components_res = requests.get(AMX_components_url, headers=header)
    index_res = requests.get(AMX_index_ohlc_url, headers=header)

    # get and clean the components
    df_components = get_components_dataframe(components_res)
    clean_components(df_components)

    # clean the index
    df_index = get_index_info(index_res)

    print("Dataframe components:\n\n{0}".format(df_components))
    if input("Save to csv?(y/n)\n") == "y":
        write_to_csv(data_file, df_components)
    
    print("\nIndex value:\n{0}".format(df_index))
    if input("Save to csv?(y/n)\n") == "y":
        write_to_csv(data_file, df_index.T)