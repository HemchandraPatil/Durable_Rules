import pandas as pd
import re
from durable.lang import *

# Load Excel file
df = pd.read_excel("/workspaces/Durable_Rules/complex_rules2.xlsx")

# Convert to list of dictionaries
rules = df.to_dict(orient="records")
#print(rules)

# Function to properly format conditions
def format_conditions(condition_expr):
    formatted_expr = condition_expr.strip()
    formatted_expr = formatted_expr.replace("AND", "and").replace("OR", "or")  
    formatted_expr = formatted_expr.replace("days_since_last_refill", "m.days_since_last_refill")  
    formatted_expr = formatted_expr.replace("stage", "m.stage")  
    return formatted_expr

# Sort rules by the highest discount first
#rules.sort(key=lambda r: float(r["Discount Value"]) if r["Discount Type"] == "Discount" else 1.0)

#Define ruleset
with ruleset("complex_rule"):
    def add_rule(rule_name,condition,action_type,action_value,discount_type,discount_value):
        formatted_conditions = format_conditions(condition)  # Fix conditions
        #print(f"Registering Rule: {rule_name} with Condition: {formatted_conditions}")

        @when_all(eval(formatted_conditions))
        def rule_action(c):
            patient_id = c.m['patient_id']
            medication = c.m['medication']
            days_since_last_refill = c.m['days_since_last_refill']
            price = c.m["price"] 

            if action_type == 'Fact' and discount_type == 'Discount':
                discount_price = price - (price * (discount_value/100))
                print(f"Discount and Reminder : We have applied {discount_value}% discount on {medication}, New price is {discount_price}. Reminder to Patient {patient_id}, please refill {medication}.")
                # assert_fact("complex_rule", {"patient_id": patient_id,
                #     "medication": medication,
                #     "days_since_last_refill": days_since_last_refill,
                #     "price":price,
                #     "stage": "reminder_sent"})
                delete_state(c)
                
            elif action_type == "Offer" and discount_type == "Discount":
                new_discount_price = price - (price * (discount_value/100))
                print(f"More Discount and Resend reminder : We have applied {discount_value}% discount on {medication}, New price is {new_discount_price}. Resend reminder to Patient {patient_id}, please refill {medication} ")
                # assert_fact("complex_rule", {"patient_id": patient_id,
                #     "medication": medication,
                #     "days_since_last_refill": days_since_last_refill,
                #     "price":price,
                #     "stage": "resent_reminder"})
                delete_state(c)
                
            elif action_type == "Escalate":
                print (f"Escalation: Patient {patient_id} has not refilled {medication} for 50+ days. Contact required.")

    #Add rules from escel
    for rule in rules:
        add_rule(rule["Rule Name"], rule["Condition"], rule["Action Type"], rule["Action Value"], rule["Discount Type"], rule["Discount Value"])


#test the engine
# message = {"patient_id":101, "medication": "Aspirin", "days_since_last_refill": 35, "price":2000}
# print("Posting Message:",message)
# post("complex_rule",message)

post("complex_rule", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 35, "price": 3000})  
# #Should send a reminder and apply 20% discount

post("complex_rule", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 45, "price":3000, "stage":"resent_reminder"})  
# #Should resend a reminder and apply 50% discount

post("complex_rule", {"patient_id": 101, "medication": "Aspirin", "days_since_last_refill": 51, "stage":"resent_reminder"})
# #Should Escalte and contact required

