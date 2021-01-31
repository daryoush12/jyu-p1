
from flask import Flask
from flask import request as req
from flask import Response
import simplejson as json
from urllib import request
from io import open
import sys
import random

app = Flask(__name__)


def GetFileData():
    try:
        return json.load(open('./data.json', 'r'))
    except:
        with request.urlopen("http://hazor.eu.pythonanywhere.com/2021/data.json") as response:
            print("file not found loading from hazor")
            return json.load(response)

class DataReader():

    def __init__(self, reset):
        if(reset == "1"):
            with request.urlopen("http://hazor.eu.pythonanywhere.com/2021/data.json") as response:
                print("Loading file from hazor")         
                self.data = json.load(response)
        else:
            self.data = GetFileData()
    
    #Palauta lista tiimien nimistä:
    def GetTeamNames(self):
        result = []
        try:
            runs = self.data['sarjat']
            for run in runs:
                for team in run['joukkueet']:
                    result.append(team['nimi'])
            resultText = ''.join("{0} \n".format(team) for team in result)
            return resultText
        except:
            print("Data not found")
            return None

    def GetTeamsArray(self):
        result = []

        try:
            runs = self.data['sarjat']
            for run in runs:
                for team in run['joukkueet']:
                    result.append(team)
            return result
        except:
            print("Data not found")
            return None

    def GetTeamsIdArray(self):
        result = []
        try:
            runs = self.data['sarjat']
            for run in runs:
                for team in run['joukkueet']:
                    result.append(team['id'])
            return result
        except:
            print("Data not found")
            return None

    #Lisää tiimi sarjaan
    def AddTeamIntoSeries(self, series, team):
        print(team['nimi'])
        try:
            for x in range(len(self.data['sarjat'])):
                print(self.data['sarjat'][x]['nimi'])
                foundName = self.data['sarjat'][x]['nimi'];
                if foundName == series:
                    print("Add")
                    self.data['sarjat'][x]['joukkueet'].append(team)
        except: ValueError("Series was not found.")

    def GenerateID(self, length):
    
        ids = self.GetTeamsIdArray()
        #Aakkoset ja numerot määritelty manuaalisesti.
        letters = ['a','b','c','d','e','f','g','h','i','j','k','l',
        'm','n','o','p','q','r','s','t','u','v','w','x','y','z']
        digits = ['1','2','3','4','5','6','7','8','9','0']
        possibleId = None
    
        #Suoritus kyky heikkenee ilmentymien kasvaessa ja siksi kyseinen ratkaisu on Naiivi.
        #Oikeasti id:n generointi voitaisiin tehdä käyttämällä uuid menetelmää.
        while(possibleId == None or possibleId in ids):
            possibleId = ''.join([random.choice(letters + digits) for n in range(length)])
    
        #Palautetaan määritellyn pitkä merkkijono
        return possibleId

    # Palauta kaikki rasti koodit:
    def GetAllPointCodes(self):
        result = ""
        for x in range(len(data['rastit'])):
            if(x == 0):
                result += "{0}".format(self.data['rastit'][x]['koodi'])
            if(str.isdigit(data['rastit'][x]['koodi'][0])):
                result += ";{0}".format(self.data['rastit'][x]['koodi'])
        return result;

    def CreateOrModifyFile(self):
        file = open('data.json', 'w')
        json.dump(self.data, file)

    def DeleteTeamFromSeries(self, series, name):
        try:
            seriesIndex = None;
            for x in range(len(self.data['sarjat'])):
                foundName = self.data['sarjat'][x]['nimi'];
                if foundName == series:
                    seriesIndex = x;

            for i in range(len(self.data['sarjat'][seriesIndex]['joukkueet'])):
                print(i)
                foundTeam = self.data['sarjat'][seriesIndex]['joukkueet'][i]
                print(foundTeam['nimi'])
                if  foundTeam['nimi'].lower() == name.lower():
                    self.data['sarjat'][seriesIndex]['joukkueet'].remove(foundTeam)

                   
        except: 
            ValueError("Value was not found")
            return None

    def GetSeriesIndex(self, series):
        for x in range(len(data['sarjat'])):
            if self.data['sarjat'][x]['nimi'] == series['nimi']:
                return x
        return None

    def GetSeriesByName(self,name):
        for possibleSeries in self.data['sarjat']: 
            test = possibleSeries['nimi']
            print(test)
            if test == name:
                return possibleSeries;
        return False    

    def GetTeamScores(self):
        teams = self.GetTeamsArray()
        rs = []
        for team in teams:
            currentScore = 0
            for checkpoint in team['rastit']:
                try:
                    test = self.GetCheckpointById(checkpoint['rasti']);
                    currentScore += int(test['koodi'][0])
                except:
                    currentScore += 0;
            rs.append({'team':team, 'score':currentScore})

        rout = ""
        rs.sort(key=lambda x: x['score'], reverse=True)

        for teamScore in rs:
            rout += "{0} ({1})\n{2}\n".format(teamScore['team']['nimi'], 
            teamScore['score'], 
            self.GetMembersAsOutput(teamScore['team']))
        return rout

    def GetMembersAsOutput(self, team):
        rs = ""

        for member in team['jasenet']:
            rs += "     {0}\n".format(member)
        return rs;

    def GetCheckpointById(self, id):
        for checkpoint in self.data['rastit']:
            if str(checkpoint['id']) == str(id):
                 return checkpoint
        return None    

@app.route('/vt1')
def main(): 
    
    name = req.args.get("nimi", "unknown")
    seriesName = req.args.get("sarja", "unknown")
    teamParticipants = req.args.getlist('jasen', type=str)

    reset = req.args.get("reset", "unknown")
    tila = req.args.get("tila", "unknown")

    print(tila, reset, name, seriesName)
    reader = DataReader(reset)

    if tila == "insert":
         if name != "unknown" and seriesName != "unknown":
            newTeam = {
                "nimi": name,
                "jasenet": teamParticipants,
                "id": reader.GenerateID(10),
                "rastit": [],
                "leimaustapa": []
            }
            reader.AddTeamIntoSeries(seriesName, newTeam)
    if tila == "delete":
            reader.DeleteTeamFromSeries(seriesName, name)
            
 
    reader.CreateOrModifyFile()
    namelist = reader.GetTeamNames()
    scores = reader.GetTeamScores()
    return Response("{0}\n{1} ".format(namelist, scores), mimetype='text/plain')
