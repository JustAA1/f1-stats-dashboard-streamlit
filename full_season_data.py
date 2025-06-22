from concurrent.futures import ThreadPoolExecutor

import all_race_data as ar
import indiv_races_data as ir
import team_colors as tc

all_team_colors = tc.all_team_colors
all_tricodes_to_driver = {}
all_indiv_pts_results = {}
all_team_pts_results = {}
all_team_name_changes = {}
all_teams_to_driver = {}
all_drivers_to_team = {}
all_race_locations = {}


def process_race_results(driver_results, tricode_to_driver, driver_to_team, race, race_num, num_races):
    for data in race:
        tricode = data["driver"][1]
        name = data["driver"][0]
        driver_team = f"{tricode}-{data['team']}"
        pts_pos = [(data["pos"], data["pts"])]
        if driver_team not in driver_results:
            driver_results[driver_team] = [None]*num_races
        if driver_results[driver_team][race_num] is None:
            driver_results[driver_team][race_num] = pts_pos
        else:
            driver_results[driver_team][race_num].append(pts_pos[0])
        tricode_to_driver[tricode] = name
        driver_to_team[name] = data['team']

    return driver_results, tricode_to_driver, driver_to_team


def get_raw_results(num_races, race_links, year):
    driver_results = {}
    tricode_to_driver = {}
    driver_to_team = {}

    for race_num in range(num_races):
        normal_race = ir.get_race_data(race_links[race_num], year)
        indiv_race_data = process_race_results(driver_results, tricode_to_driver, driver_to_team, normal_race, race_num, num_races)
        driver_results, tricode_to_driver, driver_to_team = indiv_race_data
        
        if year < 2021:  # Sprints started in 2021
            continue

        sprint_race = ir.get_race_data(race_links[race_num].replace("race-result", "sprint-results"), year)
        sprint_race_data = process_race_results(driver_results, tricode_to_driver, driver_to_team, sprint_race, race_num, num_races)
        driver_results, tricode_to_driver, driver_to_team = sprint_race_data
        
    return driver_results, tricode_to_driver, driver_to_team


def get_full_results(driver_results, tricode_to_driver, num_races):
    indiv_pts_results = {}
    team_pts_results = {}
    for tricode_team in driver_results:
        szn_results = driver_results[tricode_team]
        driver = tricode_to_driver[tricode_team[:3]]
        team = tricode_team[4:]

        for race_num in range(len(szn_results)):
            race_result = szn_results[race_num]
            if race_result is None:
                continue

            pts = float(race_result[0][1])
            pos = [race_result[0][0]]
            if len(race_result) > 1:
                pts += float(race_result[1][1])
                pos.append(race_result[1][0])

            if driver not in indiv_pts_results:
                indiv_pts_results[driver] = [None]*num_races
            indiv_pts_results[driver][race_num] = pts

            if team not in team_pts_results:
                team_pts_results[team] = [0]*num_races
            team_pts_results[team][race_num] += pts

    for driver in indiv_pts_results:
        race_pts = [pts if pts is not None else 0 for pts in indiv_pts_results[driver]]
        delta = [race_pts[0]] + [0]*(num_races-1)
        for race_num in range(1, num_races):
            delta[race_num] = race_pts[race_num]
            race_pts[race_num] += race_pts[race_num-1]
        indiv_pts_results[driver] = [race_pts, delta]

    for team in team_pts_results:
        team_pts = team_pts_results[team]
        delta = [team_pts[0]] + [0]*(num_races-1)
        for race_num in range(1, num_races):
            delta[race_num] = team_pts[race_num]
            team_pts[race_num] += team_pts[race_num-1]
        team_pts_results[team] = [team_pts, delta]

    def remove_decimals(list):
        return [int(n) if (float(n)).is_integer() else n for n in list]

    indiv_pts_results = {k:[remove_decimals(v[0]), remove_decimals(v[1])] for k,v in indiv_pts_results.items()}
    team_pts_results = {k:[remove_decimals(v[0]), remove_decimals(v[1])] for k,v in team_pts_results.items()}

    return indiv_pts_results, team_pts_results


def adjust_team_names(team_pts_results):
    team_name_change = {}

    # converts team names from 2000-2025
    names_to_remove = ["Ferrari", "Mercedes", "Renault", "Honda", "RBPT", 
                    "Cosworth", "Toyota", "BMW", "Petronas", "Ford",
                    "Asiatech", "Peugeot", "Scuderia", "Racing", "TAG", 
                    "Heuer", "BWT", "Aramco", "Kick", "European", "Acer",
                    "Playlife", "Fondmetal", "Mugen", "Supertec"]
    keys_to_del = []
    teams_to_add = {}
    for key in team_pts_results:
        names = key.split(" ")
        if len(names) == 1:
            team_name_change[names[0]] = names[0]
            continue
        team_results = team_pts_results[key]
        keys_to_del.append(key)

        for i in range(len(names)):
            if names[i] == "Racing" and i==0:
                continue
            if names[i] in names_to_remove:
                names[i] = None
        team_name = " ".join([n for n in names if n is not None])
        
        if team_name == "RBR":
            team_name = "Red Bull"
        if team_name == "STR":
            team_name = "Toro Rosso"
        
        team_name_change[key] = team_name
        teams_to_add[team_name] = team_results

    for key in keys_to_del:
        del team_pts_results[key]
    team_pts_results.update(teams_to_add) 

    
    
    return team_pts_results, team_name_change

def get_teams_with_drivers(driver_team_info):
    teams_with_drivers = {}
    for driver, team in driver_team_info.items():
        if team not in teams_with_drivers:
            teams_with_drivers[team] = []
        teams_with_drivers[team].append(driver)
    return teams_with_drivers


def get_season_data(year):
    races = ar.get_all_races(year)

    race_locations = [r[0] for r in races]
    race_links = [r[1] for r in races]

    num_races = len(race_links) 
    driver_results, tricode_to_driver, driver_to_team = get_raw_results(num_races, race_links, year)
    indiv_pts_results, team_pts_results = get_full_results(driver_results, tricode_to_driver, num_races)
    team_pts_results, team_name_change = adjust_team_names(team_pts_results)

    def sort_by_points(sort_this):
        return dict(sorted(sort_this.items(), key=lambda item: item[1][0][-1], reverse=True))
    
    indiv_pts_results = sort_by_points(indiv_pts_results)
    team_pts_results = sort_by_points(team_pts_results)

    driver_team_info = {driver:team_name_change[team] for driver, team in driver_to_team.items()}
    teams_with_drivers = get_teams_with_drivers(driver_team_info)
    
    global all_tricodes_to_driver
    global all_indiv_pts_results
    global all_team_pts_results
    global all_team_name_changes
    global all_teams_to_driver
    global all_drivers_to_team
    global all_race_locations
    
    all_tricodes_to_driver[year] = tricode_to_driver
    all_indiv_pts_results[year] = indiv_pts_results
    all_team_pts_results[year] = team_pts_results
    all_team_name_changes[year] = team_name_change
    all_teams_to_driver[year] = teams_with_drivers
    all_drivers_to_team[year] = driver_team_info
    all_race_locations[year] = race_locations

    return (tricode_to_driver, indiv_pts_results, team_pts_results, team_name_change, 
            teams_with_drivers, driver_team_info, race_locations)


def get_all_data():
    with ThreadPoolExecutor(max_workers=25) as executor:
        tasks = []
        for i in range(2000, 2025+1):
            tasks.append(executor.submit(get_season_data, i))
        executor.shutdown()
    
    global all_tricodes_to_driver
    global all_indiv_pts_results
    global all_team_pts_results
    global all_team_name_changes
    global all_teams_to_driver
    global all_drivers_to_team
    global all_race_locations

    def sort_dict(sort_this):
        return dict(sorted(sort_this.items()))

    all_tricodes_to_driver = sort_dict(all_tricodes_to_driver)
    all_indiv_pts_results = sort_dict(all_indiv_pts_results)
    all_team_pts_results = sort_dict(all_team_pts_results)
    all_team_name_changes = sort_dict(all_team_name_changes)
    all_teams_to_driver = sort_dict(all_teams_to_driver)
    all_drivers_to_team = sort_dict(all_drivers_to_team)
    all_race_locations = sort_dict(all_race_locations)
    
    return (all_tricodes_to_driver, all_indiv_pts_results, all_team_pts_results, all_team_name_changes, 
            all_teams_to_driver, all_drivers_to_team, all_race_locations, all_team_colors)
