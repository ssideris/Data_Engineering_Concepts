"""
This is a boilerplate test file for pipeline 'data_cleaning'
generated using Kedro 0.18.10.
Please add your pipeline tests here.

Kedro recommends using `pytest` framework, more info about it can be found
in the official documentation:
https://docs.pytest.org/en/latest/getting-started.html
"""
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import clean_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=clean_data,
                inputs="data",
                outputs="data_clean",
                name="clean_data_node",
            )
        ]
    )
