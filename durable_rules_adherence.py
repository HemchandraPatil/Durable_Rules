import pandas as pd
import re
from durable.lang import *

# Load rules from Excel
df = pd.read_excel("/workspaces/Durable_Rules/adherence_rules.xlsx")
rules = df.to_dict(orient="records")

# Function to properly format conditions
def format_conditions(condition_expr):
    formatted_expr = condition_expr.strip()
    formatted_expr = formatted_expr.replace("AND", "and").replace("OR", "or")  
    formatted_expr = formatted_expr.replace("days_since_last_refill", "m.days_since_last_refill")  
    formatted_expr = formatted_expr.replace("stage", "m.stage")  
    return formatted_expr

# Define ruleset
with ruleset("medication_adherence"):
    def add_rule(rule_name, condition, action_type, action_value):
        formatted_conditions = format_conditions(condition)  # Fix conditions
        #print(f"Registering Rule: {rule_name} with Condition: {formatted_conditions}")
        
        @when_all(eval(formatted_conditions))
        def rule_action(c):
            patient_id = c.m['patient_id']
            medication = c.m['medication']
            days_since_last_refill = c.m['days_since_last_refill']

            if action_type == "Fact":
                print(f"Reminder: Patient {patient_id}, please refill {medication}.")
                # assert_fact("medication_adherence", {
                #     "patient_id": patient_id,
                #     "medication": medication,
                #     "days_since_last_refill": days_since_last_refill,
                #     "stage": "reminder_sent"
                # })
                delete_state(c)

            elif action_type == "Escalate":
                print(f"Escalation: Patient {patient_id} has not refilled {medication} for 40+ days. Contact required.")

    # Add rules from Excel
    for rule in rules:
        add_rule(rule["Rule Name"], rule["Condition"], rule["Action Type"], rule["Action Value"])

# -------------------- Testing the Rule Engine --------------------
# message = {"patient_id":101, "medication": "Aspirin", "days_since_last_refill": 45}
# print("Posting Message:",message)
#post("medication_adherence",message)

post("medication_adherence", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 32})  
# #Should send a reminder

post("medication_adherence", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 45, "stage": "reminder_sent"})  
# #Should escalate the case