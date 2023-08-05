"""
This is a boilerplate pipeline 'data_science'
generated using Kedro 0.18.9
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import processing, split_data, train_model, evaluate_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([node(
        func=processing,
        inputs="cleaned_data",
        outputs="model_input_table",
        name="process_data_node",
    ), node(
        func=split_data,
        inputs=["model_input_table", "params:model_options"],
        outputs=["X_train", "X_test", "y_train", "y_test"],
        name="split_data_node",
    ), node(
        func=train_model,
        inputs=["X_train", "y_train"],
        outputs="regressor",
        name="train_model_node",
    ), node(
        func=evaluate_model,
        inputs=["regressor", "X_test", "y_test"],
        outputs=None,
        name="evaluate_model_node",
    ), ])
