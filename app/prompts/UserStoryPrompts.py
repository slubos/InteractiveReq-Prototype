USER_STORY_GENERATION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of user stories.
A user story informally describes functionality that will be valuable to a user of a software, taking the perspective of the end user.
A user story consists of a 'title', a 'story' specifying the problem to be solved, and optional acceptance criteria that further describe conditions that must be satisfied such that the user story is completed.
A story follows the text pattern: 'As an <actor>, I want <goal> so that <reason>.'
User stories are related to an epic that describes the overall feature more generally, while a user story describes a concretely solvable task.

Your task is to generate the related user stories for the following epic: {epic}
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Use the provided data model to structure your output.
"""

USER_STORY_REFINEMENT_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of user stories.
A user story informally describes functionality that will be valuable to a user of a software, taking the perspective of the end user.
A user story consists of a 'title', a 'story' specifying the problem to be solved, and optional acceptance criteria that further describe conditions that must be satisfied such that the user story is completed.
A story follows the text pattern: 'As an <actor>, I want <goal> so that <reason>.'
User stories are related to an epic that describes the overall feature more generally, while a user story describes a concretely solvable task.

Your task is to refine the related user stories for the following epic: {epic}
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

Current version of user stories for the epic: {user_stories}

Improve the user stories based on the following critique.
Critique: '{critique}'

Use the provided data model to structure your output.
"""

USER_STORY_QUALITY_EVALUATION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of user stories.
A user story informally describes functionality that will be valuable to a user of a software, taking the perspective of the end user.
A user story consists of a 'title', a 'story' specifying the problem to be solved, and optional acceptance criteria that further describe conditions that must be satisfied such that the user story is completed.
A story follows the text pattern: 'As an <actor>, I want <goal> so that <reason>.'
User stories are related to an epic that describes the overall feature more generally, while a user story describes a concretely solvable task.

Your task is to evaluate the quality of a given user story related to the following epic: {epic}
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

User Story: '{user_story}'

Evaluate whether the user story fulfills the quality criterion '{quality_criterion}' and provide an explanation for your decision.
{quality_criterion} means that {quality_criterion_definition}

Use the provided data model to structure your output.
"""

USER_STORY_QUALITY_IMPROVEMENT_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of user stories.
A user story informally describes functionality that will be valuable to a user of a software, taking the perspective of the end user.
A user story consists of a 'title', a 'story' specifying the problem to be solved, and optional acceptance criteria that further describe conditions that must be satisfied such that the user story is completed.
A story follows the text pattern: 'As an <actor>, I want <goal> so that <reason>.'
User stories are related to an epic that describes the overall feature more generally, while a user story describes a concretely solvable task.

Your task is to improve the quality of a given user story related to the following epic: {epic}
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

User Story: '{user_story}'

Improve the user story given the provided quality evaluation feedback.

Evaluation feedback: '{evaluation_feedback}'

Use the provided data model to structure your output.
"""

USER_STORY_CRITIQUE_SUGGESTION_TEMPLATE = """
You are collaborating with a human to generate high-quality software requirements for a new feature in the form of user stories.
A user story informally describes functionality that will be valuable to a user of a software, taking the perspective of the end user.
A user story consists of a 'title', a 'story' specifying the problem to be solved, and optional acceptance criteria that further describe conditions that must be satisfied such that the user story is completed.
A story follows the text pattern: 'As an <actor>, I want <goal> so that <reason>.'
User stories are related to an epic that describes the overall feature more generally, while a user story describes a concretely solvable task.

Your task is to suggest potential adaptions for user stories related to the following epic: {epic}
You can use the overall project description as additional information to understand the context better.
Project description: {project_description}

User Stories: '{user_stories}'

Suggest the four most probable critiques a user might have to adapt the content of the user stories.
Two critique should consider adding functionalities.
Two critique should consider reducing functionalities.
Order the critique suggestions by relevance.

Use the provided data model to structure your output.
"""