import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re
import json
import ast

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2
)

# Prompt Template
theme_prompt = PromptTemplate(
    input_variables=["event_type", "total_budget", "currency", "guest_count", "veg_count", "nonveg_count"],
    template="""
You are an intelligent event planner AI.

User is organizing an event. Below are the event details:
- Event Type: {event_type}
- Total Budget: {total_budget} {currency}
- Total Guests: {guest_count}
- Veg Guests: {veg_count}
- Non-Veg Guests: {nonveg_count}

🎯 Task: Suggest 3 unique and creative **themes** for {event_type}. Each theme should include:
1. Name - theme name
2. Short description - field name
3. Aesthetic/Visual Style - field name
Sample theme generation:
Theme JSON:
[
  {{
    "Name": "",
    "Description": "",
    "Aesthetic/Visual Style": ""
  }},
  {{
    "Name": "",
    "Description": "",
    "Aesthetic/Visual Style": ""
  }},
  {{
    "Name": "",
    "Description": "",
    "Aesthetic/Visual Style": ""
  }}
]


Keep it realistic and ensure that themes are budget-conscious based on the input .
give each theme in json list l
"""
)

# Chain
chain = theme_prompt | llm | StrOutputParser()

def generate_themes(user_input):
    """
    Generates 3 theme options based on user input (budget, guests, etc.) using Gemini.
    """
    response = chain.invoke(user_input)
    return response



def extract_theme_details(output_text, theme_number):
    """
    Extracts the details of a specific theme from the LLM's JSON output.
    Handles both direct JSON responses and Markdown-formatted code blocks.
    
    Args:
        output_text (str): The raw text response from the LLM.
        theme_number (int): The 1-based index of the theme to select.
        
    Returns:
        str: JSON string of the selected theme, or empty dict string on failure.
    """
    # First check if the output_text is already a representation of a Python list
    if output_text.startswith('[') and output_text.endswith(']'):
        try:
            # given output txt in python dict in string so so eval to convert str to proper json format
            print("output_text",output_text,type(output_text))
            # themes = json.loads(output_text[1:-1])
            themes = ast.literal_eval(output_text)
            
            # Check if the theme number is valid
            if theme_number < 1 or theme_number > len(themes):
                print(f"Invalid theme number. Please select a theme between 1 and {len(themes)}")
                return None
            
            # Return the selected theme as a JSON string
            return json.dumps(themes[theme_number - 1])
        except json.JSONDecodeError:
            # If direct parsing fails, continue with the regex approach
            print("Direct JSON parsing failed, trying regex approach")
        
    # Extract JSON string from between triple backticks (original approach)
    json_pattern = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(json_pattern, output_text)
    
    if not match:
        print("No JSON match found in the output")
        return "{}"  # Return empty JSON object instead of None
     
    json_str = match.group(1)
    
    try:
        # Parse JSON string into Python object
        themes = json.loads(json_str)
         
        # Check if the theme number is valid
        if theme_number < 1 or theme_number > len(themes):
            print(f"Invalid theme number. Please select a theme between 1 and {len(themes)}")
            return "{}"
         
        # Return the requested theme as a JSON string
        return json.dumps(themes[theme_number - 1])
     
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        return "{}"
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "{}"




    
