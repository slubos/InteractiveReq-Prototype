EPIC_GENERATION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of an epic.
An epic describes a larger feature to be implemented in a software, described in a general way.
An epic and consist of a 'title' and a 'description' specifying the feature and why it is needed for users of the software.
Concrete solutions for the implementation are not part of the epic.

Your task is to generate the initial version of an epic for a given project context and feature description.
Project description: {project_description}

Feature description: {feature_description}

Use the provided data model to structure your output.
"""

EPIC_REFINEMENT_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of an epic.
An epic describes a larger feature to be implemented in a software, described in a general way.
An epic and consist of a 'title' and a 'description' specifying the feature and why it is needed for users of the software.
Concrete solutions for the implementation are not part of the epic.

Your task is to refine the current epic version for a given feature description based on provided feedback.
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Feature description: {feature_description}

Current epic version: {epic}

Adapt the epic based on the provided critique.
Critique: {critique}

Use the provided data model to structure your output.
"""

EPIC_QUALITY_EVALUATION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of an epic.
An epic describes a larger feature to be implemented in a software, described in a general way.
An epic and consist of a 'title' and a 'description' specifying the feature and why it is needed for users of the software.
Concrete solutions for the implementation are not part of the epic.

Your task is to evaluate the quality of a given epic for a given feature description.
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Feature description: {feature_description}

Epic: {epic}

Evaluate whether the epic fulfills the quality criterion '{quality_criterion}' and provide an explanation for your decision.
{quality_criterion} means that {quality_criterion_definition}

Use the provided data model to structure your output.
"""

EPIC_QUALITY_IMPROVEMENT_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of an epic.
An epic describes a larger feature to be implemented in a software, described in a general way.
An epic and consist of a 'title' and a 'description' specifying the feature and why it is needed for users of the software.
Concrete solutions for the implementation are not part of the epic.

Your task is to improve the quality of a given epic for a given feature description.
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Feature description: {feature_description}

Epic: '{epic}'

Improve the epic given the provided quality evaluation feedback.

Evaluation feedback: '{evaluation_feedback}'

Use the provided data model to structure your output.
"""

EPIC_CRITIQUE_SUGGESTION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of an epic.
An epic describes a larger feature to be implemented in a software, described in a general way.
An epic and consist of a 'title' and a 'description' specifying the feature and why it is needed for users of the software.
Concrete solutions for the implementation are not part of the epic.

Your task is to suggest potential adaptions for a given epic for a given feature description.
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Feature description: {feature_description}

Epic: '{epic}'

Suggest the four most probable critiques a user might have to adapt the content of the epic.
Two critique should consider adding functionalities.
Two critique should consider reducing functionalities.
Order the critique suggestions by relevance.

Use the provided data model to structure your output.
"""