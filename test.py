import pandas as pd
import re
from durable.lang import *

# Load rules from Excel


#print("Loaded rules from Excel: ", rules)

import pandas as pd

# Load the rules from the Excel sheet
df = pd.read_excel("/workspaces/Durable_Rules/adherence_rules.xlsx")
rules = df.to_dict(orient="records")

# Evaluate conditions dynamically
def evaluate_rule(rule_condition, context):
    try:
        return eval(rule_condition, {}, context)
    except Exception as e:
        print(f"Error evaluating condition '{rule_condition}': {e}")
        return False

# Apply rules to the given data
def apply_rules(rules, context):
    for _, rule in rules.iterrows():
        condition = rule["Condition"]
        action_type = rule["Action Type"]
        action_value = rule["Action Value"]

        if evaluate_rule(condition, context):
            print(f"Rule Triggered: {rule['Rule Name']}")
            print(f"Action: {action_type} -> {action_value}")

# Example Usage
if __name__ == "__main__":
    rules_file = "rules.xlsx"  # Update with your actual file path
    rules = load_rules(rules_file)

    # Example input data
    test_data = {"days_since_last_refill": 35, "stage": "reminder_sent"}

    apply_rules(rules, test_data)