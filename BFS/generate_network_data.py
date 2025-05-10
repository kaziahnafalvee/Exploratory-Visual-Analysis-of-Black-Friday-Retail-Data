
import pandas as pd
from itertools import combinations
from collections import defaultdict
import json

#dataset
df = pd.read_csv("train.csv")

# Select only the columns needed
df = df[["User_ID", "Product_Category_1", "Product_Category_2", "Product_Category_3"]]

#Fill missing values and convert to integers, Missing product categories (especially 2 & 3) were filled with -1
#Later,ignored -1 during processing

df.fillna(-1, inplace=True)
df = df.astype(int)

#Group product categories by user, For each user, we gathered a set of categories they bought
user_category_map = defaultdict(set)
for _, row in df.iterrows():
    user_id = row["User_ID"]
    for cat in [row["Product_Category_1"], row["Product_Category_2"], row["Product_Category_3"]]:
        if cat != -1:
            user_category_map[user_id].add(cat)

# Count co-occurrences between category pairs, We computed how often each pair of categories appeared together
#Only counted unique combinations (no repetition, no self-pairs)

co_occurrence = defaultdict(int)
for categories in user_category_map.values():
    for cat1, cat2 in combinations(sorted(categories), 2):
        co_occurrence[(cat1, cat2)] += 1

# Format data, One node per product category (e.g., "Category 5")
nodes = sorted({cat for pair in co_occurrence.keys() for cat in pair})
nodes_json = [{"id": f"Category {cat}", "group": 1} for cat in nodes]


# Each co-purchase pair becomes a link, value = number of times those two categories were bought together

links_json = [
    {
        "source": f"Category {cat1}",
        "target": f"Category {cat2}",
        "value": count
    }
    for (cat1, cat2), count in co_occurrence.items() if count > 10
]

network_data = {"nodes": nodes_json, "links": links_json}

#save
with open("product_category_network.json", "w") as f:
    json.dump(network_data, f, indent=2)

print(" Network data saved as product_category_network.json")
