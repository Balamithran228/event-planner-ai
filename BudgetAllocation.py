
from themeBaseCode import (
    os,
    llm,
    StrOutputParser,
    PromptTemplate,
    re,
    json
)

def allocate_budget_with_guided_llm(user_input):
    # Define rule-based allocation ratios by event type
    allocation_guidelines = {
        "Wedding": {
            "food_ratio": "45-55%",
            "entertainment_ratio": "20-30%",
            "decorations_ratio": "20-30%",
        },
        "Birthday": {
            "food_ratio": "35-45%",
            "entertainment_ratio": "35-45%",
            "decorations_ratio": "15-25%",
        },
        "Corporate": {
            "food_ratio": "30-40%",
            "entertainment_ratio": "30-40%",
            "decorations_ratio": "25-35%",
        }
    }
    
    # Get event type and use default if not found
    event_type = user_input.get("event_type", "Wedding")
    guidelines = allocation_guidelines.get(event_type, allocation_guidelines["Wedding"])
    
    # Create a prompt that incorporates the rule-based guidelines
    prompt = PromptTemplate.from_template("""
    You are an expert event planner with knowledge of Indian wedding and event costs. Given the following event details and budget guidelines, please allocate the total budget across three categories: food, entertainment, and decorations.
    
    Event Details:
    - Event Type: {event_type}
    - Total Budget: {total_budget} {currency}
    - Number of Guests: {guest_count} (Vegetarian: {veg_count}, Non-vegetarian: {nonveg_count})
    - Theme: {theme_name}
    - Theme Description: {theme_description}
    - Theme Aesthetic: {theme_aesthetic}
    
    Budget Allocation Guidelines for {event_type}:
    - Food should typically be around {food_ratio} of the total budget
    - Entertainment should typically be around mostly defualt is {entertainment_ratio} of the total budget
    - Decorations should typically be around {decorations_ratio} of the total budget
    
    Important Considerations:
    1. For food, calculate based on the number of vegetarian and non-vegetarian guests using the per-guest cost guidelines.
    2. For a theme like "{theme_name}", adjust the decoration and entertainment allocations to best achieve the aesthetic described.
    3. The sum of all allocations must exactly equal the total budget of {total_budget} {currency}.
    4. Round all amounts to whole numbers.
    
    Return a JSON object with the following structure:
    {{
      "food": allocated_amount_for_food,
      "entertainment": allocated_amount_for_entertainment,
      "decorations": allocated_amount_for_decorations,
      "total": total_budget,
      "reasoning": "detailed explanation of your allocation decisions, including theme considerations"
    }}
    """)
    
    
    chain = prompt | llm | StrOutputParser()

    # Extract theme details for the prompt
    theme = user_input.get("theme", {})
    total_budget = user_input.get("total_budget", 0)
    
    try:
        # Invoke the chain with proper error handling
        response = chain.invoke({
            "event_type": user_input.get("event_type", "Wedding"),
            "total_budget": total_budget,
            "currency": user_input.get("currency", "INR"),
            "guest_count": user_input.get("guest_count", 100),
            "veg_count": user_input.get("veg_count", 50),
            "nonveg_count": user_input.get("nonveg_count", 50),
            "theme_name": theme.get("Name", "Classic"),
            "theme_description": theme.get("Description", "A traditional event"),
            "theme_aesthetic": theme.get("Aesthetic/Visual Style", "Elegant and simple"),
            "food_ratio": guidelines["food_ratio"],
            "entertainment_ratio": guidelines["entertainment_ratio"],
            "decorations_ratio": guidelines["decorations_ratio"],
        })
        
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            # print("Extracted JSON string:", json_str)
            response_dict = json.loads(json_str)
        else:
            # Direct parse attempt
            response_dict = json.loads(response)
        
        # Validate the allocation to ensure it matches the total budget
        actual_total = response_dict.get("food", 0) + response_dict.get("entertainment", 0) + response_dict.get("decorations", 0)
        if actual_total != total_budget:
            # Adjust to match total budget (add/subtract from largest category)
            diff = total_budget - actual_total
            max_category = max(["food", "entertainment", "decorations"], 
                              key=lambda x: response_dict.get(x, 0))
            response_dict[max_category] += diff
            response_dict["total"] = total_budget
            response_dict["reasoning"] += f" (Adjusted {max_category} by {diff} to ensure total matches budget.)"
        
        return response_dict
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        # Try to extract any valid JSON from the response
        try:
            json_pattern = r'(\{.*\})'
            match = re.search(json_pattern, response, re.DOTALL)
            if match:
                json_str = match.group(1)
                # print("Attempting to parse extracted JSON:", json_str)
                response_dict = json.loads(json_str)
                return response_dict
        except Exception as inner_e:
            print(f"Failed to extract JSON with regex: {inner_e}")
        
        # Fallback: Return a default allocation
        return {
            "food": int(total_budget * 0.45),
            "entertainment": int(total_budget * 0.25),
            "decorations": int(total_budget * 0.30),
            "total": total_budget,
            "reasoning": "Default allocation due to response parsing error",
            "error": str(e)
        }
    except Exception as e:
        print(f"Error during allocation: {e}")
        return {"error": str(e)}


def get_BudgetData(input_data):
    # Test the function
    # user_data = get_answer(input_data)
    #print("User data received:", json.dumps(user_data, indent=2))
    result = allocate_budget_with_guided_llm(input_data)

    combined_output = {
        "event_details": input_data,
        "budget_allocation": result
    }
    return combined_output

# print(get_BudgetData())