from BudgetAllocation import (
    llm,
    get_BudgetData,
    StrOutputParser,
    PromptTemplate,
    json
)
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_amazon_products_for_decorations_with_allData(response_Dict):
    # step 1 fetch busget data with event data
    print(response_Dict)
    print("31")
    # Step 2: Create Prompt Template
    prompt_template = PromptTemplate.from_template("""
    You are an expert {event_type} planner.
    Suggest 3 main decoration product search keywords on Amazon for the following: also it should be easily available.

    Event: {event_type}
    Theme: {theme_name}
    Theme Description: {theme_desc}
    Visual Style: {visual_style}
    Total Budget: {decorations_budget} {currency}
    Divide this {decorations_budget} by 3, that is the cost for each product keyword you generate.

    Just return a Python list like ["keyword1", "keyword2", amount_per_product, total_amount]
    """)
    print(response_Dict['event_details']['theme'],type(response_Dict['event_details']['theme']))
    prompt_inputs = {
        "event_type": response_Dict['event_details']['event_type'],
        "currency": response_Dict['event_details']['currency'],
        "theme_name": response_Dict['event_details']['theme']['Name'],  # Changed from 'Name' to 'theme_name'
        "theme_desc": response_Dict['event_details']['theme']['Description'],  # Changed from 'Description' to 'description'
        "visual_style": response_Dict['event_details']['theme']['Aesthetic/Visual Style'],  # Changed from 'Aesthetic/Visual Style' to 'aesthetic_visual_style'
        "decorations_budget": response_Dict['budget_allocation']['decorations'],
    }
    # Step 3: Get product keywords
    chain = prompt_template | llm | StrOutputParser()
    response = chain.invoke(prompt_inputs)
    keyword_data = eval(response[10:-4])
    # print(keyword_data)
    print("32")
    result = fetch_amazon_products_from_keywords(keyword_data)
    response_Dict["Decoration_Recommandations"] = result
    # print(json.dumps(response_Dict, indent=4, ensure_ascii=False))
    print("33")
    return response_Dict

def fetch_amazon_products_from_keywords(keyword_data):
    keywords = keyword_data[:-2]
    amount_per_product = keyword_data[-2]
    total_amount = keyword_data[-1]

    url = "https://real-time-amazon-data.p.rapidapi.com/search"

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }

    results = {
        "keywords": keywords,
        "amount_per_product": amount_per_product,
        "total_amount": total_amount,
        "products": []
    }

    for keyword in keywords:
        querystring = {
            "query":keyword,
            "page":"1",
            "country":"IN",
            "sort_by":"RELEVANCE",
            "max_price":amount_per_product,
            "product_condition":"ALL",
            "is_prime":"false",
            "deals_and_discounts":"NONE"
            }
        # print(keyword,type(keyword),amount_per_product,type(amount_per_product))


        try:
            print("fetch before")
            res = requests.get(url, headers=headers, params=querystring)
            data = res.json()
            print("fetch after")
            # print()
            # print(data)
            # print()
        except Exception as e:
            print(f"Error fetching keyword '{keyword}': {e}")
            continue

        if data.get("status") == "OK":
            keyword_products = []
            for product in data.get("data", {}).get("products", [])[:5]:  # Top 5 results
                keyword_products.append({
                    "title": product.get("product_title", "Not Available"),
                    "price": product.get("product_price", "Not Available"),
                    "url": product.get("product_url", "Not Available"),
                    "rating": product.get("product_star_rating", "Not Available"),
                    "imageUrl": product.get("product_photo", "Not Available")
                })
            results["products"].append({
                "keyword": keyword,
                "items": keyword_products
            })
        else:
            results["products"].append({
                "keyword": keyword,
                "items": [],
                "error": data.get("error", "Unknown error")
            })


    return results

# response_Dict = get_BudgetData()
# get_amazon_products_for_decorations_with_allData()
