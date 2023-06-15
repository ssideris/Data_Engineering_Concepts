"""
This is a boilerplate pipeline 'data_science'
generated using Kedro 0.18.9
"""
import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from typing import Dict, Tuple
from sklearn.linear_model import LinearRegression


def drop_cols(data: pd.DataFrame) -> pd.DataFrame:
    processed_data = data.drop(['date', 'sqft_above', 'bathrooms', ], axis=1)
    return processed_data


def scale(data: pd.DataFrame, num_cols: list) -> pd.DataFrame:
    # scale numeric
    data[num_cols] = MinMaxScaler().fit_transform(data[num_cols])
    return data


def one_hot_encode(data: pd.DataFrame, cat_cols: list) -> pd.DataFrame:
    # one-hot-encode categorical
    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore').fit(
        data[cat_cols])
    encoded_cols = encoder.get_feature_names_out(cat_cols)
    encoded_data = encoder.transform(data[cat_cols])
    # Create a DataFrame with the encoded columns
    processed_data_encoded = pd.DataFrame(encoded_data, columns=encoded_cols)
    processed_data = pd.concat([data, processed_data_encoded], axis=1)
    return processed_data


def processing(data: pd.DataFrame) -> pd.DataFrame:
    processed_data = drop_cols(data)
    num_cols = [col for col in processed_data.columns if processed_data[col].dtype in [
        'float64', 'int64']]
    cat_cols = [col for col in processed_data.columns if processed_data[col].dtype not in [
        'float64', 'int64']]
    processed_data = scale(processed_data, num_cols)
    processed_data = one_hot_encode(processed_data, cat_cols)

    return processed_data


def split_data(data: pd.DataFrame, parameters: Dict) -> Tuple:
    cat_cols = [col for col in data.columns if data[col].dtype not in [
        'float64', 'int64']]
    cat_cols.append("price")
    X = data.drop(cat_cols, axis=1)
    y = data["price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=parameters["test_size"], random_state=parameters["random_state"]
    )
    return X_train, X_test, y_train, y_test


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> LinearRegression:
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    return regressor


def evaluate_model(regressor: LinearRegression, X_test: pd.DataFrame, y_test: pd.Series):
    predicted = regressor.predict(X_test)
    score = np.sqrt(mean_squared_error(y_test, predicted))
    logger = logging.getLogger(__name__)
    logger.info("Model has RMSE equal to %f on test data.", score)
