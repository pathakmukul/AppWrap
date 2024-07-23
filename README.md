# AppWrap
AppWrap: AI-powered Streamlit tool builder that transforms natural language instructions into functional web pages. It leverages LLMs to interpret user requests, dynamically generate content, and create Streamlit components, enabling rapid prototyping of interactive web applications without coding expertise.

![image](https://github.com/user-attachments/assets/557bb108-bfac-4dc4-b3d9-5fffd1a950fa)


Natural Language Page Creation: Describe the page you want, and the AI will build it for you.
Dynamic Content Generation: Automatically generate essays and content using LLMs.
Local Page Saving: Created pages are saved locally for easy access and editing.
Streamlit Integration: Seamlessly integrates with Streamlit for interactive web applications.
Extensible Actions: Easily add new actions to expand the tool's capabilities.

How It Works

User Input: Users provide natural language instructions for page creation.
AI Processing: An AI agent interprets the instructions and decides on the appropriate actions.
Page Generation: The system executes the actions, creating Streamlit components and generating content as needed.
Local Saving: Generated pages are saved as Python files in a local pages directory.
Dynamic Loading: Streamlit dynamically loads and displays the created pages.

Key Components

main.py: The core script that handles user interactions and page management.
LLMCall.py: Manages interactions with the Groq API for content generation.
pages/: Directory where generated pages are stored.

Getting Started

Clone the repository
Install the required dependencies:
pip install streamlit python-dotenv groq

Set up your API key in a .env file
Run the Streamlit app:
streamlit run main.py


Acknowledgments

Streamlit for providing an excellent framework for creating data applications
Groq for their powerful LLM API
& of course, King GPT!

