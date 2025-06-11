# Streamlit modules to import
import streamlit as st
from streamlit_echarts import st_echarts

# Gathers Data from APIs every 12 hours (or when the app is initally started)
@st.cache_data(ttl=12*3600)
def getData():
    import fullSeason as fs
    allData = fs.getAllData()
    return allData
data = getData()
allTricodesToDriver, allIndivPtsResults, allTeamPtsResults, allTeamNameChanges, allTeamsToDriver, allDriversToTeam, allRaceLocations, allTeamColors = data

# Function to display title page
def titlePage():
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
yearOption = st.sidebar.selectbox(
    "Select year:",
    (str(n) for n in range(2025, 2000-1, -1)),
    index=None,
    placeholder="Select year...",
)

# Option to choose between drivers and constructors
selection = st.sidebar.radio(
    "Select championship:",
    ["Drivers", "Constructors"],
    disabled=(yearOption is None)  # Disable if no year is selected
)

# Display title page when no year is selected
if yearOption is None:
    titlePage()

# Function to display Constructors Standings
def constructorsStandings():
    st.title("F1 Constructors Standings")

    global yearOption; global allTeamPtsResults; global allRaceLocations; global allTeamColors
    yearOption = int(yearOption)
    
    f1Data = {
        "teamsWithPoints": allTeamPtsResults.get(yearOption),
        "raceLocations": allRaceLocations.get(yearOption)
    }

    # Create datasets for each team
    datasets = [
        {
            "id": f"dataset_{team}",
            "source": [[i, points, f1Data["raceLocations"][i], f"(+{change})"] for i, points, change in zip(range(len(points_list[0])), points_list[0], points_list[1])]
        }
        for team, points_list in f1Data["teamsWithPoints"].items()
    ]

    # Create series configuration for each team
    seriesList = [
        {
            "type": "line",
            "datasetId": f"dataset_{team}",
            "showSymbol": True,
            "name": team,
            "endLabel": {
                "show": True,
                "formatter": "{@[1]}" + f" - {team}",
                "fontSize": 12,
                "textBorderColor": allTeamColors.get(yearOption)[team],  # Team-dependent color
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
                "color": allTeamColors.get(yearOption)[team]  # Team-dependent color
            }
        }
        for team in f1Data["teamsWithPoints"].keys()
    ]

    # Configure the chart options
    option = {
        "animationDuration": 500,
        "dataset": datasets,  # Using the datasets created above
        "title": {"text": f"Year: {yearOption}"},
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
            "data": f1Data["raceLocations"]
        },
        "yAxis": {"name": "Points"},
        "grid": {"right": 100},
        "series": seriesList,
    }
    
    # Displaying the chart
    st_echarts(options=option, height="550px")

# Function to display Drivers Standings
def driverStandings():
    st.title("F1 Drivers Standings")

    global yearOption; global allIndivPtsResults; global allRaceLocations
    global allTeamColors; global allDriversToTeam
    yearOption = int(yearOption)

    f1Data = {
        "driverData": allIndivPtsResults.get(yearOption),
        "raceLocations": allRaceLocations.get(yearOption)
    }

    # Create datasets for each team
    datasets = [
        {
            "id": f"dataset_{driver}",
            "source": [[i, points, f1Data["raceLocations"][i], f"(+{change})"] for i, points, change in zip(range(len(points_list[0])), points_list[0], points_list[1])]
        }
        for driver, points_list in f1Data["driverData"].items()
    ]

    # Create series configuration for each team
    seriesList = [
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
                "color": allTeamColors.get(yearOption)[allDriversToTeam.get(yearOption)[driver]]
            }
        }
        for driver in f1Data["driverData"].keys()
    ]

    # Configure the chart options
    option = {
        "animationDuration": 500,
        "dataset": datasets,
        "title": {"text": f"Year: {yearOption}"},
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
            "data": f1Data["raceLocations"]
        },
        "yAxis": {"name": "Points"},
        "grid": {"right": 100},
        "series": seriesList,
    }

    # Create two columns: one for the chart, one for the leaderboard
    col1, col2 = st.columns([3, 1])
    
    # Rendering the chart
    with col1:
        st_echarts(options=option, height="565px", width="115%")
    
    # Display the leaderboard
    with col2:   
        for position, (driver, points) in zip(range(1, len(f1Data['driverData'])+1), f1Data['driverData'].items()):
            teamColor = allTeamColors.get(yearOption)[allDriversToTeam.get(yearOption)[driver]]
            nameSplit = driver.split()
            name = f"{nameSplit[0][0]}. {nameSplit[-1]}" if driver != "Zhou Guanyu" else "G. Zhou"
            st.markdown(
                f"<div style='display: flex; align-items: center;'>"
                f"<div style='background-color: {teamColor}; width: 10px; height: 10px; margin-right: 5px;'></div>"
                f"<span style='font-weight: bold;'>{position}: {name}</span>"
                f"<span style='margin-left: auto; margin-right: -10px;'>{points[0][-1]}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# Render the selected page
if selection == "Drivers" and yearOption:
    driverStandings()
elif selection == "Constructors" and yearOption:
    constructorsStandings()
