import pandas as pd

# Load Excel file
df = pd.read_excel("workspaces/Durable_Rules/rules.xlsx")

# Convert to list of dictionaries
rules = df.to_dict(orient="records")
print(rules)