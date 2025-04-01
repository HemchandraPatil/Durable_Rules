import pandas as pd

# Load Excel file
df = pd.read_excel("C:/Users/hemchandra.patil/Documents/rules.xlsx")

# Convert to list of dictionaries
rules = df.to_dict(orient="records")
print(rules)