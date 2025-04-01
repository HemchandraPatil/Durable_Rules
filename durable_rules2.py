import pandas as pd
from durable.lang import *

# Load Excel file
df = pd.read_excel("/workspaces/Durable_Rules/rule2.xlsx")

# Convert to list of dictionaries
rules = df.to_dict(orient="records")
print(rules)

# Map Excel operators to Python operators
op_map = {">": ">", "<": "<", ">=": ">=", "<=": "<=", "=": "=="}

# Define rulesets
with ruleset("Discount"):
    def add_rule(rule_name, condition, operator, value, action_type, action_value):
        python_operator = op_map.get(operator, "==")
        condition_expr = f"m.{condition} {python_operator} {value}"
        
        @when_all(eval(condition_expr))
        def rule_action(c):
            price = c.m['price']
            medication = c.m['medication']

            if action_type == "Discount":
                discount_price = price * float(action_value)
                print(f"Discount applied for {medication}. New price: {discount_price:.2f}")

            elif action_type == "No Discount":
                print(f"No Discount applied for {medication}. Price is {price:.2f}")

    # Add rules from Excel
    for rule in rules:
        add_rule(rule["Rule Name"], rule["Condition"], rule["Operator"], rule["value"], rule["Action Type"], rule["Action value"])

# -------------------- Testing the Rule Engine --------------------
post("Discount", {"price": 2000, "medication": "Painkiller"})  # Should apply 10% discount
post("Discount", {"price": 3500, "medication": "Antibiotic"})  # Should apply 20% discount
post("Discount", {"price": 800, "medication": "Cough Syrup"})  # Should apply no discount