import streamlit as st
from dotenv import load_dotenv
import os
import openai
import re
from pathlib import Path
from sys_prompt import system_prompt4 #(at bottom)
from LLMCall import GPTCalls, GroqCalls  # choose whats necessary. In this example we use GPT

# Load environment variables and initialize OpenAI client
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class Agent:
    def __init__(self, client: openai, system: str = ""):
        self.client = client
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            temperature=0
        )
        return completion.choices[0].message.content.strip()

# Initialize StreamBuilder with the OpenAI client and the imported system prompt
StreamBuilder = Agent(client=openai, system=system_prompt4)
if 'pages' not in st.session_state:
    st.session_state['pages'] = {}

def essay_writer(topic: str):
    essay = GroqCalls(topic)
    return {'action': 'text', 'content': essay}

def streamlit_coder(description: str):
    code_prompt = f"""
    Write Streamlit code for: {description}
    
    Make sure to include the following at the top of the file:
    from LLMCall import GroqCalls
    
    When using LLM calls, use the GroqCalls function like this:

    response = GroqCalls(prompt)
    Also concatenate the prompt for the tool in prompt variable to customise responses.
    Ensure the code is complete and executable.
    """
    code = GroqCalls(code_prompt)
    return {'action': 'code', 'content': code}

def final_reviewer(code: str):
    review_prompt = f"""
    You are a production streamlit app developer. You have been given a streamlit python code which contains
    all the necessary imports and functions. Although its not clean and few features maybe here and there.
    With what has been given to you clean the code reorder it and make it efficient. DONT ADD ANY new element to the code.
    3. Remove any unnecessary comments, text, or formatting such as ```python or ```
    4. Ensure proper indentation and correct function structure.
    5. Use correct Streamlit functions and syntax.
    6. Make sure the code is clean, efficient, and executable.
    7. Do not include any explanations or comments in your output.

    Here's the code to review and rewrite:

    {code}

    Please provide only the corrected, executable Streamlit code without any additional text or explanations.
    """
    corrected_code = GroqCalls(review_prompt)
    return {'action': 'code', 'content': corrected_code}

def llm_call(prompt: str):
    response = GroqCalls(prompt)
    return {'action': 'llm_response', 'content': response}

def manage_pages(query: str):
    actions = {
        "essay_writer": essay_writer,
        "streamlit_coder": streamlit_coder,
        "llm_call": llm_call,
    }
    next_prompt = query
    page_elements = []
    i = 0
    max_iterations = 10

    while i < max_iterations:
        i += 1
        result = StreamBuilder(next_prompt)
        print("Agent response:", result)  # Debug print

        if "PAUSE" in result and "Action" in result:
            action_search = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
            if action_search:
                chosen_tool, arg = action_search[0]
                if chosen_tool in actions:
                    element = actions[chosen_tool](arg)
                    page_elements.append(element)
                    print("Added element:", element)  # Debug print
                    next_prompt = f"Observation: {chosen_tool} added"
                else:
                    next_prompt = "Observation: Tool not found"
                continue
        if "Answer" in result:
            break

    # Combine all code elements
    combined_code = "\n".join([element['content'] for element in page_elements if element['action'] == 'code'])
    
    # Run final review on the combined code
    reviewed_code = final_reviewer(combined_code)
    
    # Replace all code elements with the reviewed code
    page_elements = [element for element in page_elements if element['action'] != 'code']
    page_elements.append(reviewed_code)

    return page_elements

def escape_string(s):
    return s.replace("'", "\\'").replace('"', '\\"')

def sanitize_function_name(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    return sanitized

def save_page(page_name: str, elements: list):
    pages_dir = Path("pages")
    pages_dir.mkdir(exist_ok=True)
    
    page_filename = f"{sanitize_function_name(page_name.lower())}.py"
    page_path = pages_dir / page_filename
    
    with page_path.open("w") as f:
        f.write("import streamlit as st\n")
        f.write("from LLMCall import GroqCalls\n\n")
        for element in elements:
            if element['action'] == 'text':
                f.write(f"st.markdown('''{escape_string(element['content'])}''')\n\n")
            elif element['action'] == 'code':
                f.write(f"{element['content']}\n\n")
            elif element['action'] == 'llm_response':
                f.write(f"st.text_area('LLM Response', '''{escape_string(element['content'])}''', height=200)\n\n")
    
    print(f"Page saved to {page_path}")  # Debug print
    return page_path

def load_pages():
    pages_dir = Path("pages")
    if pages_dir.exists():
        for page_file in pages_dir.glob("*.py"):
            page_name = page_file.stem.replace("_", " ").title()
            st.session_state['pages'][page_name] = "loaded"
    print("Loaded pages:", st.session_state['pages'])  # Debug print

def home_page():
    st.title('Streamlit App Builder')
    query = st.text_input("What would you like to add to the page?", "")
    page_name = st.text_input("Enter a name for this page:")
    if st.button('Build Page'):
        if page_name:
            elements = manage_pages(query)
            page_path = save_page(page_name, elements)
            st.session_state['pages'][page_name] = "loaded"
            st.success(f"Page '{page_name}' built and saved successfully to {page_path}!")
            st.rerun()  # Force a rerun to update the sidebar
        else:
            st.warning("Please enter a name for the page.")

def dynamic_page(page_name):
    if st.session_state['pages'][page_name] == "loaded":
        st.info(f"This is the {page_name} page. Its content is defined in the pages/{sanitize_function_name(page_name.lower())}.py file.")
    else:
        st.error(f"Error: Content for {page_name} not found.")

# Load existing pages when the app starts
load_pages()

st.sidebar.title('Navigation')
page_options = ['Home'] + list(st.session_state['pages'].keys())
selected_page = st.sidebar.selectbox('Choose a page:', page_options)

if selected_page == 'Home':
    home_page()
elif selected_page in st.session_state['pages']:
    dynamic_page(selected_page)




# system_prompt4 = """
# You run in a loop of Thought, Action, PAUSE, Observation.
# At the end of the loop you output an Answer
# Use Thought to describe your thoughts about the question you have been asked.
# Use Action to perform one of the actions available to you - then return PAUSE.
# Observation will be the result of running those actions.

# Your available actions are:

# essay_writer:
# e.g., essay_writer: The impact of artificial intelligence on modern society
# Generates and adds a 500-word essay on the specified topic to the page.

# streamlit_coder:
# e.g., streamlit_coder: Create a title saying 'Welcome to Our AI App' and add a paragraph introducing the app
# Generates Streamlit code for the specified functionality and adds it to the page. This action can be used to create any Streamlit element, including titles, text, headers, buttons, and more complex components.

# final_reviewer:
# e.g., final_reviewer: [Streamlit code to review]
# Reviews the Streamlit code, corrects any issues with indentation, structure, or Streamlit usage, and provides a cleaned-up version of the code. This step is crucial for ensuring the final code is properly formatted and executable.

# llm_call:
# e.g., llm_call: What is the capital of France?
# Makes an LLM call with the specified prompt and adds the response to the page.

# Example session:

# Question: Create a page about AI with a title, an introductory paragraph, a detailed essay, and a button to generate AI facts.
# Thought: The user wants a page about AI with several elements. I'll add these elements one by one using the streamlit_coder and essay_writer actions.
# Action: streamlit_coder: Create a title saying 'Artificial Intelligence: Shaping Our Future' and add an introductory paragraph about AI's impact on society
# PAUSE 

# You will be called again with this:

# Observation: Code added

# Thought: Now I need to add a detailed essay about AI's impact on society.
# Action: essay_writer: The impact of artificial intelligence on modern society
# PAUSE

# You will be called again with this:

# Observation: Essay added

# Thought: Lastly, I need to add a button to generate AI facts.
# Action: streamlit_coder: Create a button that, when clicked, displays a random AI fact using an LLM call
# PAUSE

# You will be called again with this:

# Observation: Code added

# Thought: Now that all elements are added, I should review and correct the code for the page to ensure it's properly structured and formatted.
# Action: final_reviewer: [Full code of the page]
# PAUSE

# You will be called again with this:

# Observation: Code reviewed and corrected

# If you have all elements as requested, output it as the Answer.

# Answer: Page created with a title, an introductory paragraph, a detailed essay about AI's impact on modern society, and an interactive button to generate AI facts. The code has been reviewed, corrected, and properly formatted to ensure it's executable.

# Remember to use these actions as needed to fulfill the user's request for page content. Always use the final_reviewer action as the last step to ensure the code is properly structured and formatted.
# """
