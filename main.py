import json
import random

# Define categories
categories = [
    "Aso Oke",
    "Casual Wear",
    "Formal Wear",
    "Footwear",
    "Accessories"
]

# Sample colors
color_palette = [
    {"name": "White", "hex": "#FFFFFF"},
    {"name": "Black", "hex": "#000000"},
    {"name": "Blue", "hex": "#0000FF"},
    {"name": "Red", "hex": "#FF0000"},
    {"name": "Green", "hex": "#008000"},
    {"name": "Gray", "hex": "#808080"},
    {"name": "Yellow", "hex": "#FFFF00"},
    {"name": "Pink", "hex": "#FFC0CB"},
    {"name": "Purple", "hex": "#800080"},
    {"name": "Brown", "hex": "#A52A2A"}
]

# Sample sizes
sizes_by_category = {
    "Aso Oke": ["S", "M", "L", "XL"],
    "Casual Wear": ["S", "M", "L", "XL"],
    "Formal Wear": ["S", "M", "L"],
    "Footwear": ["7", "8", "9", "10", "11"],
    "Accessories": ["One Size"]
}

# Sample details
details_template = [
    {"tab": "description", "content": "High-quality product for everyday use."},
    {"tab": "details", "content": "Made from durable and comfortable materials."},
    {"tab": "shipping", "content": "Delivered within 3-5 business days."}
]

products = []
for i in range(1, 61):  # 60 products
    category = random.choice(categories)
    sizes = sizes_by_category[category]

    # Pick unique colors
    colors = random.sample(color_palette, random.randint(1, 3))

    product = {
        "id": None,
        "title": f"Product {i}",
        "description": f"A premium quality {category.lower()} product number {i}.",
        "original_price": round(random.uniform(10000, 100000), 2),
        "discount_percent": random.choice([5, 10, 15, 20, 25]),
        "rating": float(random.randint(1, 5)),  # Whole number as decimal
        "category": [category],
        "sizes": sizes,
        "colors": colors,
        "details": details_template
    }
    products.append(product)

# Save to file
file_path = "/mnt/data/dummy_products.json"
with open(file_path, "w") as f:
    json.dump(products, f, indent=4)

file_path
