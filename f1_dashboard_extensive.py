import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config for a wider layout
st.set_page_config(page_title="F1 2025 Dashboard", page_icon="🏎️")

# Apply custom CSS for better styling
st.markdown(
    """
<style>
    h1 {
        color: #FF1E00;
        text-align: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF1E00;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title with F1 styling
st.title("F1 2025 SEASON DASHBOARD")

# Team colors mapping based on actual 2025 teams
TEAM_COLORS = {
    "Ferrari": "#DC0000",
    "Mercedes": "#00D2BE",
    "Red Bull Racing": "#0600EF",
    "McLaren": "#FF8700",
    "Aston Martin": "#006F62",
    "Alpine": "#0090FF",
    "Williams": "#005AFF",
    "Haas F1 Team": "#F0F0F0",
    "Kick Sauber": "#52E252",
    "VCARB": "#4E7C9B",
}


# Load drivers data for proper team-driver mapping
@st.cache_data
def load_drivers_data():
    try:
        drivers_df = pd.read_csv("f1_drivers_list_2025.csv")
        driver_to_team = dict(zip(drivers_df["FullName"], drivers_df["Team"]))
        driver_to_abbr = dict(zip(drivers_df["FullName"], drivers_df["Abbreviation"]))
        return driver_to_team, driver_to_abbr
    except:
        return {}, {}


# Load race results data
@st.cache_data
def load_race_data():
    df = pd.read_csv("f1_race_results_2025.csv")
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.title()

    # Convert Position to numeric, handling DNF
    df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
    df["Points"] = df["Points"].fillna(0)

    # Add Win and Podium columns
    df["Win"] = df["Position"] == 1
    df["Podium"] = df["Position"] <= 3

    return df


# Load data
driver_to_team, driver_to_abbr = load_drivers_data()
df = load_race_data()


# Generate driver colors based on team colors
def get_driver_colors(df):
    driver_colors = {}
    team_drivers = {}

    for driver in df["Driver"].unique():
        team = (
            df[df["Driver"] == driver]["Team"].iloc[0]
            if "Team" in df.columns
            else driver_to_team.get(driver, "Unknown")
        )

        if team not in team_drivers:
            team_drivers[team] = []
        team_drivers[team].append(driver)

    for team, drivers in team_drivers.items():
        base_color = TEAM_COLORS.get(team, "#888888")

        for i, driver in enumerate(drivers):
            if i == 0:
                driver_colors[driver] = base_color
            else:
                r = int(base_color[1:3], 16)
                g = int(base_color[3:5], 16)
                b = int(base_color[5:7], 16)
                r = min(255, int(r * 1.2))
                g = min(255, int(g * 1.2))
                b = min(255, int(b * 1.2))
                driver_colors[driver] = f"#{r:02x}{g:02x}{b:02x}"

    return driver_colors


driver_colors = get_driver_colors(df)

# Sidebar filters
st.sidebar.header("Filters")
races = sorted(df["Race"].unique())
selected_races = st.sidebar.multiselect("Select Races:", options=races, default=races)
if selected_races:
    df = df[df["Race"].isin(selected_races)]

teams = (
    sorted(df["Team"].unique())
    if "Team" in df.columns
    else sorted(driver_to_team.values())
)
selected_teams = st.sidebar.multiselect("Select Teams:", options=teams, default=teams)
if selected_teams and "Team" in df.columns:
    df = df[df["Team"].isin(selected_teams)]

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Driver Stats", "Team Performance", "Race Analysis", "Season Progress"]
)

with tab1:
    st.header("Driver Statistics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        top_driver = (
            df.groupby("Driver")["Points"].sum().sort_values(ascending=False).index[0]
        )
        st.metric(
            "Most Points", top_driver, f"{df.groupby('Driver')['Points'].sum().max()}"
        )
    with col2:
        wins_leader = df.groupby("Driver")["Win"].sum().sort_values(ascending=False)
        st.metric("Most Wins", wins_leader.index[0], f"{int(wins_leader.iloc[0])}")
    with col3:
        podium_leader = (
            df.groupby("Driver")["Podium"].sum().sort_values(ascending=False)
        )
        st.metric(
            "Most Podiums", podium_leader.index[0], f"{int(podium_leader.iloc[0])}"
        )
    with col4:
        avg_pos = df.groupby("Driver")["Position"].mean().sort_values()
        st.metric("Best Avg Position", avg_pos.index[0], f"{avg_pos.iloc[0]:.1f}")

    st.subheader("Total Points by Driver")
    driver_points = (
        df.groupby(["Driver", "Team"])["Points"]
        .sum()
        .reset_index()
        .sort_values("Points", ascending=False)
    )
    fig_points = px.bar(
        driver_points,
        x="Driver",
        y="Points",
        color="Driver",
        color_discrete_map=driver_colors,
        text="Points",
        hover_data=["Team"],
    )
    fig_points.update_layout(
        xaxis_title="Driver", yaxis_title="Total Points", showlegend=False, height=400
    )
    fig_points.update_traces(
        textposition="outside",
        texttemplate="%{text:.0f}",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=1,
    )
    st.plotly_chart(fig_points, use_container_width=True)

    st.subheader("Driver Comparison")
    col1, col2 = st.columns(2)
    with col1:
        driver_wins = (
            df.groupby("Driver")["Win"]
            .sum()
            .reset_index()
            .sort_values("Win", ascending=False)
        )
        driver_wins = driver_wins[driver_wins["Win"] > 0]
        if not driver_wins.empty:
            fig_wins = px.bar(
                driver_wins,
                x="Driver",
                y="Win",
                color="Driver",
                color_discrete_map=driver_colors,
                text="Win",
            )
            fig_wins.update_layout(
                xaxis_title="Driver", yaxis_title="Wins", showlegend=False, height=350
            )
            st.plotly_chart(fig_wins, use_container_width=True)
        else:
            st.info("No wins data available")
    with col2:
        driver_podiums = (
            df.groupby("Driver")["Podium"]
            .sum()
            .reset_index()
            .sort_values("Podium", ascending=False)
        )
        driver_podiums = driver_podiums[driver_podiums["Podium"] > 0]
        if not driver_podiums.empty:
            fig_podiums = px.bar(
                driver_podiums,
                x="Driver",
                y="Podium",
                color="Driver",
                color_discrete_map=driver_colors,
                text="Podium",
            )
            fig_podiums.update_layout(
                xaxis_title="Driver",
                yaxis_title="Podiums",
                showlegend=False,
                height=350,
            )
            st.plotly_chart(fig_podiums, use_container_width=True)
        else:
            st.info("No podium data available")

with tab2:
    st.header("Team Performance")

    st.subheader("Constructor Championship Points")
    team_points = (
        df.groupby("Team")["Points"]
        .sum()
        .reset_index()
        .sort_values("Points", ascending=False)
    )
    fig_team = px.bar(
        team_points,
        x="Team",
        y="Points",
        color="Team",
        color_discrete_map=TEAM_COLORS,
        text="Points",
    )
    fig_team.update_layout(
        xaxis_title="Team", yaxis_title="Total Points", showlegend=False, height=400
    )
    fig_team.update_traces(
        textposition="outside",
        texttemplate="%{text:.0f}",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=1,
    )
    st.plotly_chart(fig_team, use_container_width=True)

    st.subheader("Average Finish Position by Team")
    team_avg = (
        df.groupby("Team")["Position"].mean().reset_index().sort_values("Position")
    )
    fig_avg = px.bar(
        team_avg,
        x="Team",
        y="Position",
        color="Team",
        color_discrete_map=TEAM_COLORS,
        text_auto=".1f",
    )
    fig_avg.update_layout(
        xaxis_title="Team",
        yaxis_title="Average Position (Lower is Better)",
        showlegend=False,
        height=400,
        yaxis={"autorange": "reversed"},
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    st.subheader("Teammate Comparison")
    team_driver_counts = df.groupby("Team")["Driver"].nunique()
    teams_with_multiple_drivers = team_driver_counts[
        team_driver_counts > 1
    ].index.tolist()

    if teams_with_multiple_drivers:
        selected_team = st.selectbox(
            "Select Team for Teammate Comparison:", options=teams_with_multiple_drivers
        )

        if selected_team:
            team_drivers = df[df["Team"] == selected_team]["Driver"].unique().tolist()

            if len(team_drivers) >= 2:
                st.write(f"Comparison between {' and '.join(team_drivers)}")

                # Calculate head-to-head race results
                race_results = []
                for race in df["Race"].unique():
                    race_df = df[(df["Team"] == selected_team) & (df["Race"] == race)]

                    if len(race_df) == 2:
                        positions = race_df.set_index("Driver")["Position"].to_dict()
                        drivers = list(positions.keys())

                        if not any(pd.isna(pos) for pos in positions.values()):
                            sorted_drivers = sorted(
                                positions.items(), key=lambda x: x[1]
                            )
                            winner = sorted_drivers[0][0]

                            race_results.append(
                                {
                                    "Race": race,
                                    "Winner": winner,
                                    "Gap": abs(
                                        positions[drivers[0]] - positions[drivers[1]]
                                    ),
                                }
                            )

                race_results_df = pd.DataFrame(race_results)

                if not race_results_df.empty:
                    h2h_results = race_results_df["Winner"].value_counts().reset_index()
                    h2h_results.columns = ["Driver", "Races Won"]

                    fig_h2h = px.bar(
                        h2h_results,
                        x="Driver",
                        y="Races Won",
                        color="Driver",
                        color_discrete_map={
                            driver: driver_colors.get(driver, "gray")
                            for driver in team_drivers
                        },
                        title=f"{selected_team} Head-to-Head Race Results",
                        text="Races Won",
                    )
                    fig_h2h.update_layout(
                        xaxis_title="Driver",
                        yaxis_title="Races Finished Ahead",
                        showlegend=False,
                        height=400,
                    )
                    fig_h2h.update_traces(
                        textposition="outside",
                        marker_line_color="rgba(0,0,0,0.3)",
                        marker_line_width=1,
                    )
                    st.plotly_chart(fig_h2h, use_container_width=True)
                else:
                    st.info("Not enough data for head-to-head comparison.")

with tab3:
    st.header("Race Analysis")

    available_races = sorted(df["Race"].unique())
    if available_races:
        selected_race = st.selectbox("Select race to analyze:", options=available_races)

        if selected_race:
            race_df = df[df["Race"] == selected_race].sort_values("Position")

            st.subheader(f"Race Results: {selected_race}")
            st.dataframe(
                race_df[["Position", "Driver", "Team", "Points"]].reset_index(
                    drop=True
                ),
                use_container_width=True,
                height=400,
            )

            podium_df = race_df[race_df["Position"] <= 3].sort_values("Position")
            if len(podium_df) > 0:
                st.subheader("Podium")
                podium_colors = [
                    driver_colors.get(driver, "gray") for driver in podium_df["Driver"]
                ]

                col1, col2, col3 = st.columns([2, 3, 2])
                with col2:
                    fig_podium = go.Figure()
                    heights = [80, 100, 60]
                    positions = [1, 0, 2]

                    for i, (_, row) in enumerate(podium_df.iterrows()):
                        if i < 3:
                            position = row["Position"]
                            idx = int(position) - 1
                            fig_podium.add_trace(
                                go.Bar(
                                    x=[positions[idx]],
                                    y=[heights[idx]],
                                    marker_color=podium_colors[i],
                                    text=f"{row['Driver']}<br>{row['Team']}",
                                    textposition="outside",
                                    width=0.8,
                                    hoverinfo="text",
                                    hovertext=f"{int(position)}. {row['Driver']} ({row['Team']})",
                                )
                            )

                    for i, pos in enumerate([2, 1, 3]):
                        if i < len(podium_df):
                            fig_podium.add_annotation(
                                x=positions[i],
                                y=heights[i] / 2,
                                text=str(pos),
                                showarrow=False,
                                font=dict(size=24, color="white"),
                            )

                    fig_podium.update_layout(
                        title=f"{selected_race} Podium",
                        showlegend=False,
                        xaxis=dict(
                            showticklabels=False,
                            showgrid=False,
                            zeroline=False,
                            range=[-1, 3],
                        ),
                        yaxis=dict(
                            showticklabels=False, showgrid=False, zeroline=False
                        ),
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=400,
                        margin=dict(l=20, r=20, t=100, b=20),
                    )
                    st.plotly_chart(fig_podium, use_container_width=True)
    else:
        st.info("No race data available.")

with tab4:
    st.header("Championship Progress")

    race_order = {race: idx for idx, race in enumerate(df["Race"].unique(), 1)}
    df["Round"] = df["Race"].map(race_order)

    st.subheader("Driver Championship Progress")
    driver_progress = []

    for driver in df["Driver"].unique():
        driver_df = df[df["Driver"] == driver].sort_values("Round")
        if not driver_df.empty:
            cumulative_points = driver_df["Points"].cumsum()
            for i, row in driver_df.iterrows():
                driver_progress.append(
                    {
                        "Driver": driver,
                        "Team": row["Team"],
                        "Round": row["Round"],
                        "Race": row["Race"],
                        "CumulativePoints": cumulative_points[i],
                    }
                )

    driver_progress_df = pd.DataFrame(driver_progress)

    if not driver_progress_df.empty:
        fig_driver_prog = px.line(
            driver_progress_df,
            x="Round",
            y="CumulativePoints",
            color="Driver",
            color_discrete_map=driver_colors,
            hover_data=["Race", "Team"],
            markers=True,
            title="Driver Championship Points Progression",
        )
        fig_driver_prog.update_layout(
            xaxis_title="Race Number",
            yaxis_title="Cumulative Points",
            legend_title="Driver",
            height=500,
        )
        st.plotly_chart(fig_driver_prog, use_container_width=True)

        st.subheader("Constructor Championship Progress")
        team_points_by_race = (
            driver_progress_df.groupby(["Team", "Round", "Race"])["CumulativePoints"]
            .sum()
            .reset_index()
        )

        fig_team_prog = px.line(
            team_points_by_race,
            x="Round",
            y="CumulativePoints",
            color="Team",
            color_discrete_map=TEAM_COLORS,
            hover_data=["Race"],
            markers=True,
            title="Constructor Championship Points Progression",
        )
        fig_team_prog.update_layout(
            xaxis_title="Race Number",
            yaxis_title="Cumulative Points",
            legend_title="Team",
            height=500,
        )
        st.plotly_chart(fig_team_prog, use_container_width=True)
    else:
        st.info("No progression data available.")

# Footer
st.markdown(
    """
---
<p style='text-align: center; color: #888888;'>F1 2025 Season Dashboard | Created by Frank Ndungu</p>

""",
    unsafe_allow_html=True,
)
