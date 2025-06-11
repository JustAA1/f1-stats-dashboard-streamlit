from concurrent.futures import ThreadPoolExecutor

import allRaces as ar
import indivRaces as ir
import teamColors as tc

allTeamColors = tc.allTeamColors
allTricodesToDriver = {}
allIndivPtsResults = {}
allTeamPtsResults = {}
allTeamNameChanges = {}
allTeamsToDriver = {}
allDriversToTeam = {}
allRaceLocations = {}


def processRaceResults(driverResults, tricodeToDriver, driverToTeam, race, raceNum, numRaces):
    for data in race:
        tricode = data["driver"][1]
        name = data["driver"][0]
        driverTeam = f"{tricode}-{data['team']}"
        ptsPos = [(data["pos"], data["pts"])]
        if driverTeam not in driverResults:
            driverResults[driverTeam] = [None]*numRaces
        if driverResults[driverTeam][raceNum] is None:
            driverResults[driverTeam][raceNum] = ptsPos
        else:
            driverResults[driverTeam][raceNum].append(ptsPos[0])
        tricodeToDriver[tricode] = name
        driverToTeam[name] = data['team']

    return driverResults, tricodeToDriver, driverToTeam


def getRawResults(numRaces, raceLinks, year):
    driverResults = {}
    tricodeToDriver = {}
    driverToTeam = {}

    for raceNum in range(numRaces):
        normalRace = ir.getRaceData(raceLinks[raceNum], year)
        indivRaceData = processRaceResults(driverResults, tricodeToDriver, driverToTeam, normalRace, raceNum, numRaces)
        driverResults, tricodeToDriver, driverToTeam = indivRaceData
        
        if year < 2021:  # Sprints started in 2021
            continue

        sprintRace = ir.getRaceData(raceLinks[raceNum].replace("race-result", "sprint-results"), year)
        sprintRaceData = processRaceResults(driverResults, tricodeToDriver, driverToTeam, sprintRace, raceNum, numRaces)
        driverResults, tricodeToDriver, driverToTeam = sprintRaceData
        
    return driverResults, tricodeToDriver, driverToTeam


def getFullResults(driverResults, tricodeToDriver, numRaces):
    indivPtsResults = {}
    teamPtsResults = {}
    for tricodeTeam in driverResults:
        sznResults = driverResults[tricodeTeam]
        driver = tricodeToDriver[tricodeTeam[:3]]
        team = tricodeTeam[4:]

        for raceNum in range(len(sznResults)):
            raceResult = sznResults[raceNum]
            if raceResult is None:
                continue

            pts = float(raceResult[0][1])
            pos = [raceResult[0][0]]
            if len(raceResult) > 1:
                pts += float(raceResult[1][1])
                pos.append(raceResult[1][0])

            if driver not in indivPtsResults:
                indivPtsResults[driver] = [None]*numRaces
            indivPtsResults[driver][raceNum] = pts

            if team not in teamPtsResults:
                teamPtsResults[team] = [0]*numRaces
            teamPtsResults[team][raceNum] += pts

    for driver in indivPtsResults:
        racePts = [pts if pts is not None else 0 for pts in indivPtsResults[driver]]
        delta = [racePts[0]] + [0]*(numRaces-1)
        for raceNum in range(1, numRaces):
            delta[raceNum] = racePts[raceNum]
            racePts[raceNum] += racePts[raceNum-1]
        indivPtsResults[driver] = [racePts, delta]

    for team in teamPtsResults:
        teamPts = teamPtsResults[team]
        delta = [teamPts[0]] + [0]*(numRaces-1)
        for raceNum in range(1, numRaces):
            delta[raceNum] = teamPts[raceNum]
            teamPts[raceNum] += teamPts[raceNum-1]
        teamPtsResults[team] = [teamPts, delta]

    def removeDecimals(list):
        return [int(n) if (float(n)).is_integer() else n for n in list]

    indivPtsResults = {k:[removeDecimals(v[0]), removeDecimals(v[1])] for k,v in indivPtsResults.items()}
    teamPtsResults = {k:[removeDecimals(v[0]), removeDecimals(v[1])] for k,v in teamPtsResults.items()}

    return indivPtsResults, teamPtsResults


def adjustTeamNames(teamPtsResults):
    teamNameChange = {}

    # converts team names from 2000-2025
    namesToRemove = ["Ferrari", "Mercedes", "Renault", "Honda", "RBPT", 
                    "Cosworth", "Toyota", "BMW", "Petronas", "Ford",
                    "Asiatech", "Peugeot", "Scuderia", "Racing", "TAG", 
                    "Heuer", "BWT", "Aramco", "Kick", "European", "Acer",
                    "Playlife", "Fondmetal", "Mugen", "Supertec"]
    keysToDel = []
    teamsToAdd = {}
    for key in teamPtsResults:
        names = key.split(" ")
        if len(names) == 1:
            teamNameChange[names[0]] = names[0]
            continue
        teamResults = teamPtsResults[key]
        keysToDel.append(key)

        for i in range(len(names)):
            if names[i] == "Racing" and i==0:
                continue
            if names[i] in namesToRemove:
                names[i] = None
        teamName = " ".join([n for n in names if n is not None])
        
        if teamName == "RBR":
            teamName = "Red Bull"
        if teamName == "STR":
            teamName = "Toro Rosso"
        
        teamNameChange[key] = teamName
        teamsToAdd[teamName] = teamResults

    for key in keysToDel:
        del teamPtsResults[key]
    teamPtsResults.update(teamsToAdd) 

    
    
    return teamPtsResults, teamNameChange

def getTeamsWithDrivers(driverTeamInfo):
    teamsWithDrivers = {}
    for driver, team in driverTeamInfo.items():
        if team not in teamsWithDrivers:
            teamsWithDrivers[team] = []
        teamsWithDrivers[team].append(driver)
    return teamsWithDrivers


def getSeasonData(year):
    races = ar.getAllRaces(year)

    raceLocations = [r[0] for r in races]
    raceLinks = [r[1] for r in races]

    numRaces = len(raceLinks) 
    driverResults, tricodeToDriver, driverToTeam = getRawResults(numRaces, raceLinks, year)
    indivPtsResults, teamPtsResults = getFullResults(driverResults, tricodeToDriver, numRaces)
    teamPtsResults, teamNameChange = adjustTeamNames(teamPtsResults)

    def sortByPoints(sortThis):
        return dict(sorted(sortThis.items(), key=lambda item: item[1][0][-1], reverse=True))
    
    indivPtsResults = sortByPoints(indivPtsResults)
    teamPtsResults = sortByPoints(teamPtsResults)

    driverTeamInfo = {driver:teamNameChange[team] for driver, team in driverToTeam.items()}
    teamsWithDrivers = getTeamsWithDrivers(driverTeamInfo)
    
    global allTricodesToDriver
    global allIndivPtsResults
    global allTeamPtsResults
    global allTeamNameChanges
    global allTeamsToDriver
    global allDriversToTeam
    global allRaceLocations
    
    allTricodesToDriver[year] = tricodeToDriver
    allIndivPtsResults[year] = indivPtsResults
    allTeamPtsResults[year] = teamPtsResults
    allTeamNameChanges[year] = teamNameChange
    allTeamsToDriver[year] = teamsWithDrivers
    allDriversToTeam[year] = driverTeamInfo
    allRaceLocations[year] = raceLocations

    return (tricodeToDriver, indivPtsResults, teamPtsResults, teamNameChange, 
            teamsWithDrivers, driverTeamInfo, raceLocations)


def getAllData():
    with ThreadPoolExecutor(max_workers=25) as executor:
        tasks = []
        for i in range(2000, 2025+1):
            tasks.append(executor.submit(getSeasonData, i))
        executor.shutdown()
    
    global allTricodesToDriver
    global allIndivPtsResults
    global allTeamPtsResults
    global allTeamNameChanges
    global allTeamsToDriver
    global allDriversToTeam
    global allRaceLocations

    def sortDict(sortThis):
        return dict(sorted(sortThis.items()))

    allTricodesToDriver = sortDict(allTricodesToDriver)
    allIndivPtsResults = sortDict(allIndivPtsResults)
    allTeamPtsResults = sortDict(allTeamPtsResults)
    allTeamNameChanges = sortDict(allTeamNameChanges)
    allTeamsToDriver = sortDict(allTeamsToDriver)
    allDriversToTeam = sortDict(allDriversToTeam)
    allRaceLocations = sortDict(allRaceLocations)
    
    return (allTricodesToDriver, allIndivPtsResults, allTeamPtsResults, allTeamNameChanges, 
            allTeamsToDriver, allDriversToTeam, allRaceLocations, allTeamColors)
    

if __name__ == "__main__":
    xy = getSeasonData(2025)
    for y in xy:
        break
        print(y, end="\n\n\n\n")

