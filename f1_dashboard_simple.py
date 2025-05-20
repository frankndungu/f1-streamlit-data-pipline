import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Title
st.title("F1 2025 Season Stats Dashboard")

# Load CSV file
df = pd.read_csv("f1_race_results_2025.csv")

df.columns = df.columns.str.strip()  # remove any leading/trailing spaces
df.columns = df.columns.str.title()  # optional: title-case for consistency

st.write("Columns:", df.columns.tolist())  # debug print

df["Points"] = df["Points"].fillna(0)
# Total points per driver
st.subheader("🏁 Total Points by Driver")
driver_points = (
    df.groupby("Driver")["Points"].sum().sort_values(ascending=False).reset_index()
)
fig1 = sns.barplot(data=driver_points, x="Points", y="Driver", palette="viridis")
st.pyplot(fig1.figure)

# Wins per driver
st.subheader("🥇 Wins by Driver")
df["Win"] = df["Position"] == 1
driver_wins = (
    df.groupby("Driver")["Win"].sum().sort_values(ascending=False).reset_index()
)
fig2 = sns.barplot(data=driver_wins, x="Win", y="Driver", palette="rocket")
st.pyplot(fig2.figure)

# Avg team position
st.subheader("🏎️ Average Finish by Team")
team_avg = df.groupby("Team")["Position"].mean().sort_values().reset_index()
fig3 = sns.barplot(data=team_avg, x="Position", y="Team", palette="coolwarm")
st.pyplot(fig3.figure)
