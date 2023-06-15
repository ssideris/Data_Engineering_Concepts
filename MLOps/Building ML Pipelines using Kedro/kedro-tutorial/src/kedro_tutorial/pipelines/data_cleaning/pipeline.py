"""
This is a boilerplate pipeline 'data_cleaning'
generated using Kedro 0.18.10
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import clean_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([node(
        func=clean_data,
        inputs="data",
        outputs="cleaned_data",
        name="clean_data_node",
    ), ])
