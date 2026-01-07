from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
# Import your existing functions from their respective files
from themeBaseCode import generate_themes,extract_theme_details
from BudgetAllocation import get_BudgetData,json
from EventKeyGenAmazonLink import get_amazon_products_for_decorations_with_allData


# Define the state schema
class GraphState(TypedDict):
    event_data: Dict[str, Any]
    themes_json: Dict[str, Any]
    selected_theme_index: int
    event_details: Dict[str, Any]
    budget_allocation: Dict[str, Any]
    Decoration_Recommandations: Dict[str, Any]


# def select_theme_node(state: GraphState) -> GraphState:
#     print("1")
#     print(state)
#     selected_index = state.get("selected_theme_index", 1)
#     selected_theme = extract_theme_details(str(state["themes_json"]), selected_index)
#     state["event_data"]["theme"] = json.loads(selected_theme)
#     print(type(state["event_data"]),type(state["event_data"]["theme"]))
#     print("11")
#     r = {"event_details": state["event_data"]}
#     print(r)
#     return r
# import json

# def select_theme_node(state: GraphState) -> GraphState:
#     print("1")
#     print(state)

#     # Get the selected index and extract the theme details
#     selected_index = state.get("selected_theme_index", 1)
#     selected_theme = extract_theme_details(str(state["themes_json"]), selected_index)
#     r = json.loads(selected_theme)
#     print("Selected Theme:", selected_theme," 122")  # Print the selected theme to debug
#     print(selected_theme,type(selected_theme))
#     print(json.loads(selected_theme),type(json.loads(selected_theme)))
#     # Check if selected_theme is not empty and seems to be valid JSON
#     if selected_theme.strip():  # Check if the string is not empty
#         try:
#             # Try to load the theme string into a Python dictionary
#             state["event_data"]["theme"] = json.loads(selected_theme)
#             print(type(state["event_data"]), type(state["event_data"]["theme"]))
#         except json.JSONDecodeError as e:
#             print(f"Error decoding JSON: {e}")
#             state["event_data"]["theme"] = {"error": "Invalid theme data"}
#             print("Fallback to error data:", state["event_data"]["theme"])
#     else:
#         print("Selected theme is empty!")
#         state["event_data"]["theme"] = {"error": "Theme data is missing"}
    
#     print("11")
#     r = {"event_details": state["event_data"]}
#     print(r)
    
#     return r

def select_theme_node(state: GraphState) -> GraphState:
    print("1")
    print(state)

    # Get the selected index and extract the theme details
    selected_index = state.get("selected_theme_index", 1)
    
    # Try to extract theme details
    selected_theme = extract_theme_details(str(state["themes_json"]), selected_index)
    print(selected_theme,type(selected_theme))
    
    if selected_theme is None or selected_theme == "{}":
        print("Failed to extract theme details, providing default empty theme")
        state["event_data"]["theme"] = {"error": "Theme data is missing"}
    else:
        try:
            # Try to load the theme string into a Python dictionary
            theme_data = json.loads(selected_theme)
            state["event_data"]["theme"] = theme_data
            print("Selected Theme:", theme_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            state["event_data"]["theme"] = {"error": "Invalid theme data"}
            print("Fallback to error data:", state["event_data"]["theme"])
    
    print("11")
    r = {"event_details": state["event_data"]}
    print(r)
    
    return r

# Wrapper for get_BudgetData() from file2
def budget_node(state: GraphState) -> GraphState:
    """
    Calls the existing get_BudgetData() function and updates the state.
    """
    print("2")
    print(state)
    # We pass the event data to get_BudgetData
    event_details = state.get("event_details", {})
    
    # Call the existing function
    budget_result = get_BudgetData(event_details)
    print(budget_result)
    return budget_result
    # Return updated state with both event data and budget data


# Wrapper for get_amazon_products_for_decorations_with_allData() from file3
def decoration_node(state: GraphState) -> GraphState:
    """
    Calls the existing get_amazon_products_for_decorations_with_allData() function
    and updates the state.
    """
    print("3")
    # We need to pass both event and budget data to this function
    combined_data = {
        "event_details": state.get("event_details", {}),
        "budget_allocation": state.get("budget_allocation", {})
    }
    
    # Call the existing function
    decoration_result = get_amazon_products_for_decorations_with_allData(combined_data)
    print(decoration_result)

    return decoration_result

def create_event_planning_graph():
    workflow = StateGraph(GraphState)
    

    # workflow.add_node("theme_generation", generate_themes_node)
    workflow.add_node("theme_selection", select_theme_node)  # <-- YOUR NEW NODE
    workflow.add_node("budget_step", budget_node)
    workflow.add_node("decoration_step", decoration_node)

    # workflow.add_edge("theme_generation", "theme_selection")
    workflow.add_edge("theme_selection", "budget_step")
    workflow.add_edge("budget_step", "decoration_step")
    workflow.add_edge("decoration_step", END)

    
    # Set the entrypoint correctly - this is the key fix
    workflow.set_entry_point("theme_selection")
    
    # Compile the graph
    return workflow.compile()


# Function to run the graph with initial input
def run_event_planning(graph_state: GraphState):
    # Create the graph
    graph = create_event_planning_graph()
    
    # Run the graph
    result = graph.invoke(graph_state)
    
    return result

