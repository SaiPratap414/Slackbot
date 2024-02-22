import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Ensure environment variables are loaded
load_dotenv()

def draft_email(user_input, name="pratap"):
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    template = """
    You are a helpful assistant that drafts an email reply based on a new email.

    Your goal is to help the user quickly create a perfect email reply.

    Keep your reply short and to the point and mimic the style of the email so you reply in a similar manner to match the tone.

    Start your reply by saying: "Hi {name}, here's a draft for your reply:". And then proceed with the reply on a new line.

    Make sure to sign off with {signature}.
    """

    
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = "Here's the email to reply to and consider any other comments from the user for the reply as well: {user_input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    response = chain.run(user_input=user_input, signature=signature, name=name)

    return response

def generate_project_description(user_input):
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    template = """
    You are an experienced project manager. Your expertise lies in breaking down project descriptions into actionable tasks. Utilize your organizational skills to generate a detailed list of project tasks based on the user's provided description. Ensure each task is clearly defined, achievable, and contributes to the overall project goals. Leverage your project management knowledge to create a well-structured plan. Additionally, create a user task in our project management system for the relevant employee, detailing the assigned task, deadlines, and any specific instructions. Specify any additional details or requirements you would like to be considered in the task list.

    **Project Description:**
    
    {user_input}

    **Tasks:**

    1. Define Project Objectives:
        - Clearly outline the goals and objectives of the project.

    2. Identify Stakeholders:
        - Compile a list of project stakeholders and their roles.

    3. Conduct Project Kickoff Meeting:
        - Schedule and conduct a kickoff meeting to align everyone on project expectations.

    4. Create Project Schedule:
        - Develop a detailed project schedule outlining key milestones and deadlines.

    5. Resource Planning:
        - Determine the required resources for each project phase.

    6. Risk Analysis:
        - Identify potential risks and create a risk mitigation plan.

    7. Task Breakdown:
        - Break down the project into smaller, manageable tasks.

    8. Assign Responsibilities:
        - Clearly define roles and responsibilities for each team member.

    9. Communication Plan:
        - Establish a communication plan to keep all stakeholders informed.

    10. Quality Assurance Plan:
        - Develop a plan to ensure the quality of project deliverables.

    **Create User Task in Project Management System:**

    - **Task Name:** [Replace with task name]
    - **Description:** [Replace with task description]
    - **Deadline:** [Replace with task deadline]
    - **Assigned to:** [Replace with assignee]
    - **Instructions:** [Replace with task instructions]

    **Additional Details or Requirements:**
    [Replace with any additional details]

    *Note: This is a preliminary task list. Please review and provide any specific instructions or additional details for each task.*
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = "{user_input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    response = chain.run(user_input=user_input)

    return response




def get_anime_waifu_image():
    try:
        api_url = "https://api.waifu.pics/sfw/waifu"  # API endpoint for fetching a random anime waifu image
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            waifu_image_url = data.get("url")
            return waifu_image_url
        else:
            return "Sorry, I couldn't fetch an anime waifu image at the moment."
    except Exception as e:
        print(f"Error fetching anime waifu image: {e}")
        return "An error occurred while fetching the image."
