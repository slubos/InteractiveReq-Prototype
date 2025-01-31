PROJECT_CONTEXT_SUMMARIZATION = """
You are an expert for the functionality implemented in a given software project.
Your task is to summarize the context of the software project based on the features that are already implemented.
The implemented features are provided as epics with related user stories.
An epic describes a larger feature to be implemented in a software, described in a general way.
An epic and consist of a 'title' and a 'description' specifying the feature and why it is needed for users of the software.
Concrete solutions for the implementation are not part of the epic.
A user story informally describes functionality that will be valuable to a user of a software, taking the perspective of the end user.
A user story consists of a 'title', a 'story' specifying the problem to be solved, and optional acceptance criteria that further describe conditions that must be satisfied such that the user story is completed.
A story follows the text pattern: 'As an <actor>, I want <goal> so that <reason>.'
User stories are related to an epic that describes the overall feature more generally, while a user story describes a concretely solvable task.

Describe the software project including its main functionality and purpose in a few sentences the following implemented epics and user stories.

Implemented Epics and User Stories: '{epics_and_user_stories}'.

Use the provided data model to structure your output.
"""