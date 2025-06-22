# Streamlit modules to import
import streamlit as st
from streamlit_echarts import st_echarts


# Gathers Data from APIs every 12 hours (or when the app is initally started)
@st.cache_data(ttl=12*3600)
def get_data():
    import full_season_data as fs
    all_data = fs.get_all_data()
    return all_data
data = get_data()
all_tricodes_to_driver, all_indiv_pts_results, all_team_pts_results, all_team_name_changes, all_teams_to_driver, all_drivers_to_team, all_race_locations, all_team_colors = data


# Function to display title page
def title_page():
    # Basic info section
    st.header("Welcome to the F1 Standings Dashboard!")
    st.write("""
    This app provides up-to-date and historical standings for the Formula 1 Drivers and Constructors Championships, 
    allowing you to explore how your favorite drivers and teams are performing or how they have performed historically. 
    The dashboard offers various visualizations and insights to help you understand the points distribution and trends across the races for a particular season.

    ### Key Features:
    - **Real-time Standings**: Get the latest updates on this season's Drivers' and Constructors' Championship standings.
    - **Interactive Charts**: Visualize the points earned by each team and driver over the course of the season.
    - **Historical Data**: Dive into past seasons to see how teams and drivers have performed historically. 
        * Currently supports 2000-2025 with more seasons on the way!
    - **Customizable**: Easily switch between Drivers and Constructors Championship standings.
    """)

    # Create two columns
    col1, col2 = st.columns([3, 2])

    # Some info on how to use the dashboard
    with col1:
        st.write("""
        ### How to use the dashboard:
        - Use the sidebar to select the year and championship you want to view.
        - The dashboard will automatically update to show the standings for the selected year and championship.
        - You can hover over the points to see the exact points and the change from the previous race.
        """)

    # Displays an image as a dashboard preview
    with col2:
        st.image("https://i.postimg.cc/3RQzm9yg/Screenshot-2024-09-01-at-13-00-13.png", caption="Dashboard Preview")

# Sidebar title
st.sidebar.title("F1 Standings")

# Year selection in sidebar
year_option = st.sidebar.selectbox(
    "Select year:",
    (str(n) for n in range(2025, 2000-1, -1)),
    index=None,
    placeholder="Select year...",
)

# Option to choose between drivers and constructors
selection = st.sidebar.radio(
    "Select championship:",
    ["Drivers", "Constructors"],
    disabled=(year_option is None)  # Disable if no year is selected
)

# Display title page when no year is selected
if year_option is None:
    title_page()

# Function to display Constructors Standings
def constructors_standings():
    st.title("F1 Constructors Standings")

    global year_option; global all_team_pts_results; global all_race_locations; global all_team_colors
    year_option = int(year_option)
    
    f1_data = {
        "teamsWithPoints": all_team_pts_results.get(year_option),
        "raceLocations": all_race_locations.get(year_option)
    }

    # Create datasets for each team
    datasets = [
        {
            "id": f"dataset_{team}",
            "source": [[i, points, f1_data["raceLocations"][i], f"(+{change})"] for i, points, change in zip(range(len(points_list[0])), points_list[0], points_list[1])]
        }
        for team, points_list in f1_data["teamsWithPoints"].items()
    ]

    # Create series configuration for each team
    series_list = [
        {
            "type": "line",
            "datasetId": f"dataset_{team}",
            "showSymbol": True,
            "name": team,
            "endLabel": {
                "show": True,
                "formatter": "{@[1]}" + f" - {team}",
                "fontSize": 12,
                "textBorderColor": all_team_colors.get(year_option)[team],  # Team-dependent color
                "textBorderWidth": 2,
                "color": "black",
            },
            "labelLayout": {"moveOverlap": "shiftY"},
            "emphasis": {"focus": "series"},
            "encode": {
                "x": 0,
                "y": 1,
                "tooltip": [1, 3]
            },
            "itemStyle": {
                "color": all_team_colors.get(year_option)[team]  # Team-dependent color
            }
        }
        for team in f1_data["teamsWithPoints"].keys()
    ]

    # Configure the chart options
    option = {
        "animationDuration": 500,
        "dataset": datasets,  # Using the datasets created above
        "title": {"text": f"Year: {year_option}"},
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "nameLocation": "middle",
            "axisLabel": {
                "rotate": 45,  # Rotating race location labels 45 degrees
                "formatter": "{value}",
                "fontSize": 11,
                "fontWeight": "bold"
            },
            "data": f1_data["raceLocations"]
        },
        "yAxis": {"name": "Points"},
        "grid": {"right": 100},
        "series": series_list,
    }
    
    # Displaying the chart
    st_echarts(options=option, height="550px")


# Function to display Drivers Standings
def driver_standings():
    st.title("F1 Drivers Standings")

    global year_option; global all_indiv_pts_results; global all_race_locations
    global all_team_colors; global all_drivers_to_team
    year_option = int(year_option)

    f1_data = {
        "driverData": all_indiv_pts_results.get(year_option),
        "raceLocations": all_race_locations.get(year_option)
    }

    # Create datasets for each team
    datasets = [
        {
            "id": f"dataset_{driver}",
            "source": [[i, points, f1_data["raceLocations"][i], f"(+{change})"] for i, points, change in zip(range(len(points_list[0])), points_list[0], points_list[1])]
        }
        for driver, points_list in f1_data["driverData"].items()
    ]

    # Create series configuration for each team
    series_list = [
        {
            "type": "line",
            "datasetId": f"dataset_{driver}",
            "showSymbol": True,
            "name": driver,
            "endLabel": {
                "show": False,
                "formatter": "{@[1]}" + f" - {driver}",
            },
            "labelLayout": {"moveOverlap": "shiftY"},
            "emphasis": {"focus": "series"},
            "encode": {
                "x": 0,
                "y": 1,
                "tooltip": [1, 3]
            },
            "itemStyle": {
                "color": all_team_colors.get(year_option)[all_drivers_to_team.get(year_option)[driver]]
            }
        }
        for driver in f1_data["driverData"].keys()
    ]

    # Configure the chart options
    option = {
        "animationDuration": 500,
        "dataset": datasets,
        "title": {"text": f"Year: {year_option}"},
        "tooltip": {
            "show": True,
            "trigger": "item",
        },
        "xAxis": {
            "type": "category",
            "nameLocation": "middle",
            "axisLabel": {
                "rotate": 45,  # Rotate race location labels 45 degrees
                "formatter": "{value}",
                "fontSize": 10,
                "fontWeight": "bold"
            },
            "data": f1_data["raceLocations"]
        },
        "yAxis": {"name": "Points"},
        "grid": {"right": 100},
        "series": series_list,
    }

    # Create two columns: one for the chart, one for the leaderboard
    col1, col2 = st.columns([3, 1])
    
    # Rendering the chart
    with col1:
        st_echarts(options=option, height="565px", width="115%")
    
    # Display the leaderboard
    with col2:   
        for position, (driver, points) in zip(range(1, len(f1_data['driverData'])+1), f1_data['driverData'].items()):
            team_color = all_team_colors.get(year_option)[all_drivers_to_team.get(year_option)[driver]]
            name_split = driver.split()
            name = f"{name_split[0][0]}. {name_split[-1]}" if driver != "Zhou Guanyu" else "G. Zhou"
            st.markdown(
                f"<div style='display: flex; align-items: center;'>"
                f"<div style='background-color: {team_color}; width: 10px; height: 10px; margin-right: 5px;'></div>"
                f"<span style='font-weight: bold;'>{position}: {name}</span>"
                f"<span style='margin-left: auto; margin-right: -10px;'>{points[0][-1]}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# Render the selected page
if selection == "Drivers" and year_option:
    driver_standings()
elif selection == "Constructors" and year_option:
    constructors_standings()