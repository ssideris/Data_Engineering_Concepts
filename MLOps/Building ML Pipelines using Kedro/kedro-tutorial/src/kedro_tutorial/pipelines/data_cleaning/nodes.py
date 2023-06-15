"""
This is a boilerplate pipeline 'data_cleaning'
generated using Kedro 0.18.10
"""
import pandas as pd


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data_clean = data.dropna()
    data_clean = data_clean[data_clean['price'] != 0]

    return data_clean
