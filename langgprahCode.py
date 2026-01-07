from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
# Import your existing functions from their respective files
from themeBaseCode import generate_themes,extract_theme_details
from BudgetAllocation import get_BudgetData,json
from EventKeyGenAmazonLink import get_amazon_products_for_decorations_with_allData


# Define the state schema
class GraphState(TypedDict):
    """
    Represents the state of the event planning graph.
    Attributes:
        event_data: Raw event data.
        themes_json: JSON string containing generated themes.
        selected_theme_index: Index of the selected theme (1-based).
        event_details: Processed event details including selected theme.
        budget_allocation: storage for budget breakdown.
        Decoration_Recommandations: Storage for Amazon product recommendations.
    """
    event_data: Dict[str, Any]
    themes_json: Dict[str, Any]
    selected_theme_index: int
    event_details: Dict[str, Any]
    budget_allocation: Dict[str, Any]
    Decoration_Recommandations: Dict[str, Any]


def select_theme_node(state: GraphState) -> GraphState:
    """
    Node to select a specific theme from the generated options.
    It parses the theme JSON and updates the event details in the state.
    """

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
    
    r = {"event_details": state["event_data"]}
    return r

# Wrapper for get_BudgetData() from file2
def budget_node(state: GraphState) -> GraphState:
    """
    Calls the existing get_BudgetData() function and updates the state.
    """
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
    """
    Constructs the LangGraph workflow for event planning.
    Nodes:
        - theme_selection: Selects the user-preferred theme.
        - budget_step: Allocates budget based on event details.
        - decoration_step: Suggests Amazon products for decorations.
    Flow:
        theme_selection -> budget_step -> decoration_step -> END
    """
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

