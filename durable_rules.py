import pandas as pd
from durable.lang import *

# Load Excel file
df = pd.read_excel("/workspaces/Durable_Rules/rules.xlsx")

# Convert to list of dictionaries
rules = df.to_dict(orient="records")
print(rules)


# # Define rule engine
# with ruleset("age_rules"):
#     op_map = {"=": "==", ">": ">", "<": "<", ">=": ">=", "<=": "<="}

#     def create_rule(rule_name, condition, op, value, action):
#         """Function to dynamically define a rule"""
#         condition_expr = f"m.{condition} {op} {value}"

#         @when_all(eval(f"m.{condition} {op} {value}"))
#         def dynamic_rule(c):
#             print(f"Rule '{rule_name}' fired! Action: {action}")

#     # Register rules dynamically
#     for rule in rules:
#         rule_name = rule["Rule Name"]
#         condition = rule["Condition"]
#         operator = rule["Operator"]
#         value = rule["value"]
#         action = rule["Action"]

#         op = op_map.get(operator, "==")
#         create_rule(rule_name, condition, op, value, action)

# # Insert facts to trigger rules
# post("age_rules", {"age": 20})  # Should print "Adult"
# post("age_rules", {"age": 15})  # Should print "Minor"


# Map Excel operators to Python operators
op_map = {">": ">", "<": "<", ">=": ">=", "<=": "<=", "=": "=="}

# Define rule engine
with ruleset("age_rules"):
    
    # Function to add rules dynamically
    def add_rule(rule_name, condition, operator, value, action):
        python_operator = op_map.get(operator, "==")  # Get Python equivalent
        condition_expr = f"m.{condition} {python_operator} {value}"  # Create condition string
        
        @when_all(eval(condition_expr))  # Apply the condition
        def rule_action(c):
            print(f"Rule '{rule_name}' triggered! Action: {action}")

    # Loop through the Excel rules and add them to the engine
    for rule in rules:
        add_rule(rule["Rule Name"], rule["Condition"], rule["Operator"], rule["value"], rule["Action"])

# Test the rule engine
post("age_rules", {"age": 20})  # Should trigger "Adult"
post("age_rules", {"age": 15})  # Should trigger "Minor"