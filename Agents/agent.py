import os
import requests

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from Agents import structure_output
from Agents.github_api import GitHubAPI  # Import the GitHubAPI class
from Agents.structure_output import ValidationOutput, IssueOutput, IssuesOutput

from Service.TextInjectorService import TextInjectorService

load_dotenv()
nvapi_key = os.getenv('NVAPI_KEY')

# print("Entrez votre idée de projet")
# project_idea = input()


class BaseAgent:
    prompt = None
    response = None

    def __init__(self, name="BaseAgent", struct_output=None):
        self.name = name
        self.structure_output = struct_output
        self.llm_with_output_structure = (ChatNVIDIA(model="meta/llama-3.1-405b-instruct", api_key=nvapi_key)
                                          .with_structured_output(struct_output))

    def invoke_llm(self, input_text):
        # Logic to invoke the LLM with the template prompt
        content_creator = (self.prompt | self.llm_with_output_structure)
        return content_creator.invoke(input_text)


class ValidationAgent(BaseAgent):
    prompt_template = """
    ### [INST]

    You are an expert in IT project management and you are responsible.
    Your task is to understand and propose a summary of the idea, and give a name for the repository project.

    Project :
    ------
    {project_idea}
    ------

    The output message MUST use the following format :
    '''
    Title: The name of the repository project without space (replace it by underscore) 
    Description: The description of the repository project
    '''
    Begin!
    [/INST]
     """

    def __init__(self, name="ValidationAgent", token=""):
        super().__init__(name, ValidationOutput)
        self.prompt = PromptTemplate(
            input_variables=['project_idea'],
            template=self.prompt_template
        )

        self.github_api = GitHubAPI(os.getenv('GITHUB_TOKEN'))  # Initialize GitHubAPI with token

        self.reformulated_input = None  # Store the reformulated input
        self.repo_name = None  # Store the repository name

    def reformulate_input(self, project_idea):

        # Invoke the LLM to get the title and description
        self.response = self.invoke_llm({"project_idea": project_idea})

        # Logic to reformulate input for validation
        self.reformulated_input = f"{self.response.Reformulated}"
        print(self.reformulated_input)
        TextInjectorService.write(self.reformulated_input)
        return self.reformulated_input

    def create_github_repo(self, token=""):
        # Call the GitHubAPI to create a repository using the extracted repo name
        if token != "":
            self.github_api = GitHubAPI(token)

        name = self.response.Title
        if name:
            success = self.github_api.create_repo(name, private=False,
                                                  description="Repository created by ValidationAgent")
            self.repo_name = name
            return success
        else:
            print("Repository name is not set.")
            return False


class ProductOwnerAgent(BaseAgent):
    prompt_template = """
        ### [INST]


        You are an expert in IT project management and you are the product owner.
        Your task is to split the task of the project into subtasks and divide it into the most little subtask possible.
        The task has to be technical task for the development
        Task limit = 5

        Project :
        ------
        {project_reformulate}
        ------

        The output message MUST use the following format :
        '''
        Issues: List of issues that you will generated
        For one issue follow this : 
            Title: The name of the issue with the prefix feat: or bug: depending on the category 
            Description: The description of the functionality and the result to display
            Labels: A list of labels that are available on GitHub and correspond to the issue
        '''
        Begin!
        [/INST]
    """

    def __init__(self, name="ProductOwnerAgent"):
        super().__init__(name, IssuesOutput)
        self.prompt = PromptTemplate(
            input_variables=['project_reformulate'],
            template=self.prompt_template
        )

    def split_task(self, project):
        # Logic to split the task into smaller tasks
        self.response = self.invoke_llm({"project_reformulate" : project})
        print(self.response.Issues)

    def create_issues(self, repo_name, token):
        github_api = GitHubAPI(token)  # Initialize GitHubAPI with token
        for subtask in self.response.Issues:
            print(subtask.Title)
            title = subtask.Title  # Create a title for the issue
            body = subtask.Description  # Create a body for the issue
            labels = subtask.Labels  # Example label, you can modify this as needed
            github_api.create_issue(repo_name, title, body, labels)
