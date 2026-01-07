# Event Planner AI

A Streamlit-based application that uses AI to help users plan events. It leverages LangGraph for orchestration, Google Gemini for theme generation and budget allocation, and RapidAPI for fetching real-time Amazon product recommendations for decorations.

## 🚀 Setup Instructions

1.  **Clone the repository** (if applicable) or navigate to the project directory.
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment**:
    - Windows: `venv\Scripts\activate`
    - Mac/Linux: `source venv/bin/activate`
4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Set up environment variables**:
    - Create a `.env` file in the root directory.
    - Add your Google API Key:
      ```
      GOOGLE_API_KEY=your_google_ai_api_key
      ```
      *(Note: The Amazon RapidAPI key is currently configured in `EventKeyGenAmazonLink.py`, ensure you have a valid subscription if you wish to change it).*
6.  **Run the application**:
    ```bash
    streamlit run main.py
    ```

## 📂 Project Structure

-   **`main.py`**: The entry point of the application. It handles the Streamlit UI, user input, and displays the final event plan.
-   **`langgprahCode.py`**: Defines the LangGraph workflow that orchestrates the event planning process.
-   **`themeBaseCode.py`**: Contains logic for generating creative event themes using Google Gemini.
-   **`BudgetAllocation.py`**: Handles the intelligent allocation of the layout budget across different categories.
-   **`EventKeyGenAmazonLink.py`**: Fetches product recommendations from Amazon based on the theme and budget.

## 📜 Key Functions

### `main.py` (Frontend)
-   `load_event_plan(json_data)`: Helper to load event plan data.
-   `display_event_details(event_details)`: Renders the "Overview" tab with metrics like guest count, budget, and additional details.
-   `display_theme(theme)`: Shows the selected theme, description, visual style, and color palette.
-   `display_budget(budget_allocation)`: Visualizes the budget distribution using a table and a bar chart.
-   `display_decorations(decoration_data)`: Displays recommended decoration products with images, prices, and links to Amazon.
-   `main()`: The main execution loop of the Streamlit app.

### `langgprahCode.py` (Orchestrator)
-   `create_event_planning_graph()`: Constructs the state graph with nodes for theme selection, budgeting, and decorations.
-   `run_event_planning(graph_state)`: Compiles and invokes the graph with the initial user state.
-   **Nodes**:
    -   `select_theme_node(state)`: Processes the user's selected theme.
    -   `budget_node(state)`: Calls the budget allocation logic.
    -   `decoration_node(state)`: Calls the product recommendation logic.

### `themeBaseCode.py` (Theme Generation)
-   `generate_themes(user_input)`: Uses LLM to generate 3 unique theme options based on event type and budget.
-   `extract_theme_details(output_text, theme_number)`: Parses the LLM's JSON response to retrieve the specific theme selected by the user.

### `BudgetAllocation.py` (Budgeting)
-   `allocate_budget_with_guided_llm(user_input)`: Uses LLM to calculate budget splits (Food, Entertainment, Decorations) based on predefined ratios and the specific event theme.
-   `get_BudgetData(input_data)`: Wrapper function to integrate with the graph state.

### `EventKeyGenAmazonLink.py` (Product Search)
-   `get_amazon_products_for_decorations_with_allData(response_Dict)`: Generates search keywords using LLM and then fetches products.
-   `fetch_amazon_products_from_keywords(keyword_data)`: Calls the RapidAPI Amazon Data service to get real product listings for the generated keywords.
