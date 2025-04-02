import pandas as pd
import re
from durable.lang import *

# Load Excel file
df = pd.read_excel("/workspaces/Durable_Rules/complex_rules2.xlsx")

# Convert to list of dictionaries
rules = df.to_dict(orient="records")

# Function to properly format conditions
def format_conditions(condition_expr):
    formatted_expr = condition_expr.strip()
    formatted_expr = formatted_expr.replace("AND", "and").replace("OR", "or")
    formatted_expr = formatted_expr.replace("days_since_last_refill", "m.days_since_last_refill")
    formatted_expr = formatted_expr.replace("stage", "m.stage")
    return formatted_expr

# Track processed patient-stage pairs to avoid duplicate rule execution
processed_rules = set()

# Define ruleset
with ruleset("complex_rule"):
    def add_rule(rule_name, condition, action_type, action_value, discount_type, discount_value):
        formatted_conditions = format_conditions(condition)

        @when_all(eval(formatted_conditions))
        def rule_action(c):
            patient_id = c.m['patient_id']
            medication = c.m['medication']
            days_since_last_refill = c.m['days_since_last_refill']
            price = c.m.get('price', 0)  # Default to 0 if price is missing
            stage = c.m.get('stage', None)
            
            print(f"Processing Rule: {rule_name} for Patient {patient_id} with condition {formatted_conditions}")
            
            # Avoid duplicate execution for the same rule-stage pair
            key = (patient_id, medication, stage, rule_name)
            if key in processed_rules:
                return
            processed_rules.add(key)

            if action_type == 'Fact' and discount_type == 'Discount':
                discount_price = price - (price * (discount_value/100))
                print(f"Reminder: Applied {discount_value}% discount on {medication}. New price: {discount_price}.")
                assert_fact("complex_rule", {
                    "patient_id": patient_id,
                    "medication": medication,
                    "days_since_last_refill": days_since_last_refill,
                    "price": discount_price,
                    "stage": "reminder_sent"
                })
            
            elif action_type == "Offer" and discount_type == "Discount":
                discount_price = price - (price * (discount_value/100))
                print(f"More Discount: Applied {discount_value}% discount on {medication}. New price: {discount_price}.")
                assert_fact("complex_rule", {
                    "patient_id": patient_id,
                    "medication": medication,
                    "days_since_last_refill": days_since_last_refill,
                    "price": discount_price,
                    "stage": "resent_reminder"
                })
            
            elif action_type == "Escalate":
                print(f"Escalation: Patient {patient_id} has not refilled {medication} for 50+ days. Contact required.")
    
    # Add rules from Excel
    for rule in rules:
        add_rule(rule["Rule Name"], rule["Condition"], rule["Action Type"], rule["Action Value"], rule["Discount Type"], rule["Discount Value"])

# Test the engine
assert_fact("complex_rule", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 35, "price": 2000, "stage": "reminder_sent"})
post("complex_rule", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 45, "price": 3000, "stage": "reminder_sent"})
post("complex_rule", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 51, "stage": "resent_reminder"})
