# InteractiveReq - Prototype and Dataset

This repository accompanies the UMAP 2025 paper *InteractiveReq: Enhancing User Story Specifications with Critiquing-based Recommender Systems*.

It contains a command-line prototype and the dataset used in our evaluation.

## Repository Structure
- **`dataset/`** - Contains the datasets used in the paper.
- **`app/`** - Includes the CLI prototype.
- **`app/workflows/`** - Implements the workflow logic.
- **`app/prompts/`** - Defines the prompts used by the system.
- **`sample_result/`** - Includes an example for generated project description and requirements.

## Configuration
This application uses an LLM hosted on [Replicate](https://replicate.com). To run the application:

1. Create an API token on Replicate.
2. Add the token to `config.yaml` under:
   ```yaml
   config["llm"]["api_token"]
   ```

### Dependencies
Install the required dependencies with:
```sh
pip install -r requirements.txt
```

## Running the Application
To start the CLI application, run:
```sh
python main.py
```

### Usage
1. The CLI prompts you to provide a file with implemented requirements (e.g., `../dataset/calculator/requirements.json`).
   - If you prefer to start a new project, press Enter and provide a description in the next step.
2. Enter a high-level feature description, e.g., *Add square root computation*.
3. Follow the interactive CLI instructions to generate detailed requirements.

This tool helps refine user story specifications through an interactive, critiquing-based approach. The generated project description and requirements are exported as `JSON` files.

