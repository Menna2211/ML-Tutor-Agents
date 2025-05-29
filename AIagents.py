import os
from dotenv import load_dotenv
import yaml
from agents import (Agent, AsyncOpenAI, OpenAIResponsesModel, FileSearchTool)

# Load .env variables (for local development)
load_dotenv()

vector_store_id = "vs_682cb69bf5d08191b77f78f2693aa591"

def load_agent_config(yaml_file_path):
    """Load agent configuration from YAML file."""
    
    with open(yaml_file_path, 'r', encoding="utf-8") as file:
        return yaml.safe_load(file)

def initialize_agents(api_key):
    """Initialize all agents with the provided API key."""
    if not api_key:
        return None, None, None, None
    
    # Initialize the model with the provided API key
    llm_model = OpenAIResponsesModel(
        model="gpt-4.1-mini", 
        openai_client=AsyncOpenAI(api_key=api_key)
    )
    
    # Load configurations from YAML files
    professor_config = load_agent_config('professor_agent.yaml')
    storytelling_config = load_agent_config('Elaboration_agent.yaml')
    argument_config = load_agent_config('argument_agent.yaml')
    case_study_config = load_agent_config('case_study_agent.yaml')
    
    # Create agents using YAML configurations
    professor_agent = Agent(
        name=professor_config['name'],
        instructions=professor_config['instructions'],
        model=llm_model,
        tools=[
            FileSearchTool(
                max_num_results=10,
                vector_store_ids=[vector_store_id],
                include_search_results=True,
            )
        ],
    )
    
    storytelling_agent = Agent(
        name=storytelling_config['name'],
        instructions=storytelling_config['instructions'],
        model=llm_model,
        tools=[
            FileSearchTool(
                max_num_results=10,
                vector_store_ids=[vector_store_id],
                include_search_results=True,
            )
        ],
    )
    
    argument_agent = Agent(
        name=argument_config['name'],
        instructions=argument_config['instructions'],
        model=llm_model,
        tools=[
            FileSearchTool(
                max_num_results=10,
                vector_store_ids=[vector_store_id],
                include_search_results=True,
            )
        ],
    )
    
    case_study_agent = Agent(
        name=case_study_config['name'],
        instructions=case_study_config['instructions'],
        model=llm_model,
        tools=[
            FileSearchTool(
                max_num_results=10,
                vector_store_ids=[vector_store_id],
                include_search_results=True,
            )
        ],
    )
    
    return professor_agent, storytelling_agent, argument_agent, case_study_agent
