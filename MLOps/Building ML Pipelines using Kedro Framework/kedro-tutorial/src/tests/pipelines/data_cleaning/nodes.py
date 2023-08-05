import pandas as pd


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Cleans the Raw Data after the EDA"""
    data_clean = data[data['price'] != 0]
    return data_clean
