import streamlit as st
import json
import pandas as pd
import re
from urllib.parse import quote
from langgprahCode import run_event_planning
from themeBaseCode import extract_theme_details,generate_themes
from langgprahCode import select_theme_node,GraphState

def load_event_plan(json_data=None):
    """Load event plan from JSON data or file upload."""
    if json_data:
        try:
            if isinstance(json_data, str):
                return json.loads(json_data)
            return json_data
        except json.JSONDecodeError:
            st.error("Invalid JSON data. Please check the format.")
            return None
    return None

def display_event_details(event_details):
    """Display event details in a clean format."""
    st.header("📅 Event Details")
    
    # Extract the basic details
    event_type = event_details.get("event_type", "Not specified")
    total_budget = event_details.get("total_budget", 0)
    currency = event_details.get("currency", "")
    guest_count = event_details.get("guest_count", 0)
    
    # Create metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Event Type", event_type)
        st.metric("Guest Count", guest_count)
    
    with col2:
        st.metric("Total Budget", f"{currency} {total_budget:,}" if currency else f"{total_budget:,}")
        
        # Check if veg/nonveg counts exist
        if "veg_count" in event_details and "nonveg_count" in event_details:
            st.metric("Vegetarian Guests", event_details["veg_count"])
    
    with col3:
        if "food_guest_per_person" in event_details:
            st.metric("Food Budget per Person", f"{currency} {event_details['food_guest_per_person']}" if currency else f"{event_details['food_guest_per_person']}")
        
        if "nonveg_count" in event_details:
            st.metric("Non-Vegetarian Guests", event_details["nonveg_count"])
    
    # Display any additional fields in expander
    additional_fields = {k: v for k, v in event_details.items() 
                        if k not in ["event_type", "total_budget", "currency", 
                                    "guest_count", "veg_count", "nonveg_count", 
                                    "food_guest_per_person", "theme"]}
    
    if additional_fields:
        with st.expander("Additional Details"):
            for key, value in additional_fields.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

def display_theme(theme):
    """Display theme information dynamically."""
    if not theme:
        st.warning("No theme information available")
        return
    
    st.header("🎨 Theme")
    
    # Theme name and description - handle different key structures
    theme_name = theme.get("theme_name", theme.get("Name", "Theme Not Available"))
    theme_description = theme.get("description", theme.get("Description", "No description available"))
    
    st.subheader(theme_name)
    st.write(theme_description)
    
    # Visual style - handle different key structures
    visual_style = theme.get("aesthetic_visual_style", theme.get("Aesthetic/Visual Style", None))
    if visual_style:
        with st.expander("Aesthetic & Visual Style", expanded=True):
            st.write(visual_style)
    
    # Extract color palette if mentioned
    if visual_style:
        colors = []
        color_keywords = ["blue", "green", "purple", "red", "yellow", "orange", 
                         "pink", "teal", "white", "black", "grey", "gray", 
                         "brown", "gold", "silver", "neon"]
        
        # Simple color extraction
        for color in color_keywords:
            if color in visual_style.lower():
                colors.append(color)
        
        if colors:
            st.subheader("Color Palette")
            color_cols = st.columns(len(colors))
            for i, color in enumerate(colors):
                with color_cols[i]:
                    # Create a color swatch
                    st.markdown(
                        f"""
                        <div style='background-color: {color}; 
                                  width: 50px; 
                                  height: 50px; 
                                  border-radius: 50%; 
                                  margin: auto;'></div>
                        <p style='text-align: center;'>{color.title()}</p>
                        """, 
                        unsafe_allow_html=True
                    )

def display_budget(budget_allocation):
    """Display budget allocation with chart."""
    if not budget_allocation:
        st.warning("No budget information available")
        return
        
    st.header("💰 Budget Allocation")
    
    # Get the main budget categories
    categories = []
    amounts = []
    
    # Extract all numeric categories
    for key, value in budget_allocation.items():
        if key.lower() != "total" and key.lower() != "reasoning":
            try:
                # Check if value is a number
                amount = float(value)
                categories.append(key.title())
                amounts.append(amount)
            except (ValueError, TypeError):
                pass
    
    # Create and display budget table
    if categories and amounts:
        budget_df = pd.DataFrame({
            "Category": categories,
            "Amount": amounts
        })
        
        # Calculate percentages
        total = budget_allocation.get("total", sum(amounts))
        budget_df["Percentage"] = budget_df["Amount"].apply(lambda x: f"{(x/total)*100:.1f}%")
        
        # Display as table
        st.table(budget_df)
        
        # Display as chart
        st.subheader("Budget Distribution")
        st.bar_chart(budget_df.set_index("Category")["Amount"])
    
    # Display reasoning if available
    if "reasoning" in budget_allocation:
        with st.expander("Budget Reasoning", expanded=True):
            # Format the reasoning text into paragraphs
            reasoning_text = budget_allocation["reasoning"]
            paragraphs = reasoning_text.split("\n\n")
            
            for paragraph in paragraphs:
                st.write(paragraph)

def display_decorations(decoration_data):
    """Display decoration recommendations."""
    if not decoration_data:
        st.warning("No decoration recommendations available")
        return
    
    st.header("✨ Decoration Recommendations")
    
    # Get the total decoration budget
    total_amount = decoration_data.get("total_amount", 0)
    amount_per_product = decoration_data.get("amount_per_product", 0)
    
    # Show budget info
    st.info(f"Total Decoration Budget: ₹{total_amount:,}")
    
    if "products" not in decoration_data or not decoration_data["products"]:
        st.warning("No specific products found in recommendations")
        return
    
    # Create tabs for each product category
    product_categories = decoration_data["products"]
    
    if len(product_categories) == 1:
        # If only one category, don't use tabs
        display_product_category(product_categories[0], amount_per_product)
    else:
        # Create tabs for multiple categories
        tabs = st.tabs([cat.get("keyword", f"Category {i+1}") for i, cat in enumerate(product_categories)])
        
        for i, tab in enumerate(tabs):
            with tab:
                display_product_category(product_categories[i], amount_per_product)

def display_product_category(category, budget_per_category):
    """Display products for a specific category."""
    keyword = category.get("keyword", "Unknown Category")
    items = category.get("items", [])
    error = category.get("error", None)
    
    st.subheader(keyword)
    st.write(f"Budget allocated: ₹{budget_per_category:,}")
    
    if error:
        st.warning(f"Error retrieving products: {error}")
        return
    
    if not items:
        st.info("No products found for this category")
        return
    
    # Display products in a grid
    cols_per_row = 3
    
    for i in range(0, len(items), cols_per_row):
        # Create a row of columns
        cols = st.columns(cols_per_row)
        
        # Fill each column with a product
        for j in range(cols_per_row):
            if i + j < len(items):
                item = items[i + j]
                with cols[j]:
                    # Display image if available
                    if "imageUrl" in item and item["imageUrl"]:
                        st.image(item["imageUrl"], use_container_width=True)
                    else:
                        # Create placeholder
                        placeholder_text = quote(keyword.split()[0])
                        st.image(f"https://via.placeholder.com/200x150?text={placeholder_text}")
                    
                    # Product info
                    title = item.get("title", "No title")
                    if len(title) > 60:
                        display_title = title[:57] + "..."
                    else:
                        display_title = title
                    
                    # Make title clickable to Amazon
                    url = item.get("url", "#")
                    st.markdown(f"**[{display_title}]({url})**")
                    
                    # Price and rating
                    price = item.get("price", "Price not available")
                    rating = item.get("rating")
                    
                    st.write(f"**Price:** {price}")
                    
                    if rating:
                        try:
                            rating_float = float(rating)
                            st.write(f"**Rating:** {'⭐' * int(rating_float)} ({rating})")
                        except (ValueError, TypeError):
                            st.write(f"**Rating:** Not available")
                    else:
                        st.write("**Rating:** Not available")
                    
                    # Add Buy button
                    if url != "#":
                        st.markdown(f"[Buy on Amazon]({url})")

def main():
    st.set_page_config(
        page_title="Event Planner AI",
        page_icon="🎉",
        layout="wide"
    )
    
    # Custom CSS to make it look nice
    st.markdown("""
    <style>
    .main {
        background-color: #f9f7fe;
    }
    h1, h2 {
        color: #6c5ce7;
    }
    h3 {
        color: #8566e5;
    }
    .stButton button {
        background-color: #6c5ce7;
        color: white;
    }
    .stExpander {
        background-color: #fff;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App title
    st.title("🎉 Event Planner AI")
    st.subheader("Your personalized event planning assistant")
    
    # Sidebar for data input
    st.sidebar.header("Load Event Plan")

    event_type = st.sidebar.text_input(
            "Event Type",
            value="Birthday Party"  # Default value
    )
    total_budget = st.sidebar.number_input(
        "Total Budget (in INR)",
        min_value=0,
        value=100000  # Default budget
    )
    guest_count = st.sidebar.number_input(
        "Total Guests",
        min_value=1,
        value=100  # Default guests
    )
    food_guest_per_person = st.sidebar.number_input(
        "Cost per Guest for Food",
        min_value=0,
        value=200  # Default cost per guest
    )

    veg_count = st.sidebar.number_input(
        "Number of Veg Guests",
        min_value=0,
        value=60  # Default veg guests
    )

    nonveg_count = st.sidebar.number_input(
        "Number of Non-Veg Guests",
        min_value=0,
        value=40  # Default non-veg guests
    )

    event_plan = None
    if total_budget > 0 and guest_count > 0:
        user_input = {
                "event_type": event_type,
                "total_budget": total_budget,
                "currency": "INR",
                "guest_count": guest_count,
                "food_guest_per_person": food_guest_per_person,
                "veg_count": veg_count,
                "nonveg_count": nonveg_count
            }

    # Generate Themes Button
    if st.sidebar.button("Generate Themes"):
        theme_output = generate_themes(user_input)
        print(theme_output)
        json_pattern = r"```json\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, theme_output)
        
        if match:
            themes_json = json.loads(match.group(1))
            st.session_state["themes"] = themes_json
            st.session_state["theme_output"] = theme_output
            st.session_state["user_input"] = user_input
        else:
            st.error("Couldn't parse themes. Try again.")

    # Theme selection
    if "themes" in st.session_state:
        theme_names = [f"{i+1}. {t['Name']}" for i, t in enumerate(st.session_state["themes"])]
        selected_index = st.sidebar.selectbox("Select a Theme", options=list(range(len(theme_names))), format_func=lambda x: theme_names[x])
        
        if st.sidebar.button("Confirm and Continue Planning"):
            st.session_state["selected_theme_index"] = selected_index + 1
            graph_state: GraphState = {
                "event_data": st.session_state["user_input"],
                "themes_json": st.session_state["themes"],
                "selected_theme_index": st.session_state["selected_theme_index"],  # if user selected the 3rd theme: "Around the World in an Evening"
                "event_details": {},
                "budget_allocation": {},
                "Decoration_Recommandations": {}
            }
            # st.json(st.session_state["themes"])
            # st.json(graph_state)
            event_plan = run_event_planning(graph_state)


    
    # Display the event plan if available
    if not event_plan:
        st.info("Please provide event planning data via one of the sidebar options")
        return
    
    # Get event type for dynamic title
    event_type = event_plan.get("event_details", {}).get("event_type", "Event")
    
    # Navigation tabs with dynamic naming
    tab1, tab2, tab3 = st.tabs(["Overview", "Budget", "Decorations"])
    
    with tab1:
        # Display event details
        if "event_details" in event_plan:
            display_event_details(event_plan["event_details"])
            
            # Display theme if available
            if "theme" in event_plan["event_details"]:
                display_theme(event_plan["event_details"]["theme"])
    
    with tab2:
        # Display budget allocation
        if "budget_allocation" in event_plan:
            display_budget(event_plan["budget_allocation"])
    
    with tab3:
        # Check for various decoration key naming patterns
        decoration_keys = [k for k in event_plan.keys() if any(term in k.lower() for term in ["decoration", "recomm", "decor"])]
        
        if decoration_keys:
            display_decorations(event_plan[decoration_keys[0]])
        else:
            st.warning("No decoration recommendations found in the event plan")
    
    # Add download and share options in sidebar
    st.sidebar.header("Actions")
    
    if st.sidebar.button(f"Export {event_type} Plan"):
        st.sidebar.info("PDF export functionality would be implemented here")
    
    if st.sidebar.button("Share with Vendors"):
        event_slug = event_plan.get("event_details", {}).get("event_type", "event").lower().replace(" ", "-")
        st.sidebar.success("Generated shareable link for vendors")
        st.sidebar.code(f"https://event-planner.ai/share/{event_slug}-{123}")
    
    # Add contact form
    st.sidebar.header("Need Help?")
    st.sidebar.text_input("Your Name")
    st.sidebar.text_input("Your Email")
    st.sidebar.text_area("Your Message")
    if st.sidebar.button("Send"):
        st.sidebar.success("Message sent! We'll get back to you soon.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center;'>
            <p>Event Planner AI © 2025 | Powered by AI | Making event planning easier</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()