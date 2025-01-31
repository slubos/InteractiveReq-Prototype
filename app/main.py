import asyncio
import os
from datetime import datetime

import click
import json
import logging.config
import yaml
from llama_index.llms.replicate import Replicate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.models.Requirements import Requirements
from app.services.RequirementsIndexGenerator import RequirementsIndexGenerator
from app.workflows.EpicGenerationWorkflow import EpicGenerationWorkflow
from app.workflows.FeatureDescriptionWorkflow import FeatureDescriptionWorkflow
from app.workflows.ProjectContextWorkflow import ProjectContextWorkflow
from app.workflows.UserStoryGenerationWorkflow import UserStoryGenerationWorkflow


def load_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
        return config

@click.command()
@click.option("--requirements", prompt="Please provide the file path to the description of implemented requirements (submit a whitespace if you want to start without prior requirements)", help="Implemented requirements path")
@click.option("--project", prompt="Please provide a textual description of the project and functionality that is currently implemented (optional if requirements file is provided, submit a whitespace to skip)", help="Textual project description")
@click.option("--feature", prompt="Please provide a textual description of the feature you would like to add", help="Textual feature description")
def cli(requirements, project, feature):
    # Load configuration
    config_path = "config.yaml"
    config = load_config(config_path)

    # Configure logging
    logging.config.dictConfig(config["logging"])
    logger = logging.getLogger(__name__)
    logger.info("Logging is configured successfully. Start Application ...")

    asyncio.run(main(requirements, project, feature))

async def main(requirements, project, feature):
    # Load configuration
    config_path = "config.yaml"
    config = load_config(config_path)

    # Configure LLM
    os.environ["REPLICATE_API_TOKEN"] = config["llm"]["api_token"]
    llm = Replicate(
        model=config["llm"]["model"],
        temperature=config["llm"]["temperature"],
        is_chat_model=config["llm"]["is_chat_model"],
    )

    # Used to name generated data
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Check if requirements file was specified
    if not requirements.isspace():
        # Configure Embedding model
        embed_model = HuggingFaceEmbedding(model_name=config["embedding"]["model"])
        requirements_index_generator = RequirementsIndexGenerator(embed_model=embed_model)
        requirements_index = requirements_index_generator.load_index(requirements)

        project_context_workflow = ProjectContextWorkflow(llm, requirements_index, timeout=600, verbose=False)
        project_description = await project_context_workflow.run(feature_descriptions=[feature])

        with open(f"generated_project_description_{timestamp}.json", "w") as json_file:
            json.dump(project_description.dict(), json_file)

        click.echo("\n---- GENERATED PROJECT DESCRIPTION ----")
        click.echo(project_description.project_description)
        project = project_description.project_description

    feature_description_workflow = FeatureDescriptionWorkflow(llm=llm, timeout=600, verbose=False)
    feature_description = await feature_description_workflow.run(project_description=project, feature_descriptions=[feature])
    click.echo("\n---- REFINED FEATURE DESCRIPTION ----")
    click.echo(feature_description)

    click.echo("\nIn the next step, an initial version of the epic is generated...")
    epic_generation_workflow = EpicGenerationWorkflow(llm=llm, timeout=6000, verbose=False)
    generated_epic = await epic_generation_workflow.run(project_description=project, feature_description=feature_description)
    click.echo("\n---- GENERATED EPIC ----")
    click.echo(f"{generated_epic.title}\nDescription: {generated_epic.description}\n")

    click.echo("\nIn the next step, an initial version of the user stories is generated. This may take some time...")
    user_story_generation_workflow = UserStoryGenerationWorkflow(llm=llm, timeout=6000, verbose=False)
    generated_requirement = await user_story_generation_workflow.run(project_description=project, epic=generated_epic)
    # Export the generated requirement to JSON
    with open(f"generated_requirements_{timestamp}.json", "w") as json_file:
        json.dump(generated_requirement.dict(), json_file)

    click.echo("\n---- GENERATED USER STORIES ----")

    for user_story in generated_requirement.epics[0].user_stories:
        click.echo(f"{user_story.title}\n{user_story.story}\nAcceptance Criteria:")
        for acceptance_criterion in user_story.acceptance_criteria:
            click.echo(f"- {acceptance_criterion}")
        click.echo("\n")

if __name__ == '__main__':
    cli()
