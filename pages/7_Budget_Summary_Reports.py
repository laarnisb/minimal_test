import pandas as pd
import matplotlib.pyplot as plt

# Sample budget vs actual data
data = {
    "Category": ["Needs", "Wants", "Savings"],
    "Budgeted": [50, 30, 20],
    "Actual": [52, 28, 20]
}

df = pd.DataFrame(data)

# Plotting side-by-side bar chart
fig, ax = plt.subplots()
bar_width = 0.35
index = range(len(df))

ax.bar(index, df["Budgeted"], bar_width, label='Budgeted')
ax.bar([i + bar_width for i in index], df["Actual"], bar_width, label='Actual')

ax.set_xlabel("Category")
ax.set_ylabel("Percentage")
ax.set_title("Budgeted vs Actual Spending")
ax.set_xticks([i + bar_width / 2 for i in index])
ax.set_xticklabels(df["Category"])
ax.legend()

plt.tight_layout()
plt.show()
