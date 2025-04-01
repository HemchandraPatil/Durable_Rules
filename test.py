import pandas as pd
import re
from durable.lang import *

# Load rules from Excel
df = pd.read_excel("/workspaces/Durable_Rules/adherence_rules.xlsx")
rules = df.to_dict(orient="records")

print("Loaded rules from Excel: ", rules)