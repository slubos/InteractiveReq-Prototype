FEATURE_DESCRIPTION_EVALUATION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature.
Your task is to evaluate the textual description of a feature and decide whether the information is sufficient to understand it.
You should consider the input insufficient if it misses critical information regarding the user need in the context of the software project, otherwise consider it sufficient.

You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Decide whether the feature description is sufficient and request further information if needed.

Feature description: '{feature_description}'.

Use the provided data model to structure your output.
"""

FEATURE_DESCRIPTION_AGGREGATION_AND_IMPROVEMENT = """
You are collaborating with a human to generate high-quality software requirements for a new feature.
The feature description is collected in multiple iterations.
Your task is to aggregate the retrieved information to a complete textual description without losing information.

You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Generate the feature description that considers the actual need in the context of the software project.
Feature descriptions: '{feature_descriptions}'.

Use the provided data model to structure your output.
"""
