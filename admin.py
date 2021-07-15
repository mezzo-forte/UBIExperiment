import os 
import json
from datetime import datetime

pathInfo = os.path.join(os.getcwd(), 'info.json')
pathDataFolder = os.path.join(os.getcwd(), 'data')
pathAdmin = os.path.join(os.getcwd(), 'expresults.json')

def load_data(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.loads(f.read())


def save_json(path, data):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=2))


def subject_counter():
    return load_data(os.path.join(os.getcwd(), 'info.json'))['Subjects']

def finished_subject_counter_and_saver():
    info = load_data(os.path.join(os.getcwd(), 'info.json'))
    counter = 0
    for i in info['IDlist']:
        pathData=os.path.join(pathDataFolder, f"{i}.json")
        dummyDict = load_data(pathData)
        if "FinishTime" in dummyDict: 
            
            counter+=1
            dummyDictAdmin = load_data(pathAdmin)
            dummyDictAdmin[i]=dummyDict
            save_json(pathAdmin, dummyDictAdmin)
    return counter    

def model_counter():
    dummyDictAdmin = load_data(pathAdmin)
    counter=[0,0,0]
    for i in dummyDictAdmin:
        if dummyDictAdmin[i]['Model']=="UBI":
            counter[0] += 1
        elif dummyDictAdmin[i]['Model']=="UBIWS":
            counter[1] += 1
        elif dummyDictAdmin[i]['Model'] == "MIGWS":
            counter[2] += 1
    return counter

def average_paid_counter(modelCounter):
    dummyDictAdmin = load_data(pathAdmin)
    sumPaid = [0,0,0]
    averagePaid = [0,0,0]
    for i in dummyDictAdmin:
        if dummyDictAdmin[i]['Model']=="UBI":
            sumPaid[0] += dummyDictAdmin[i]['PaidHours']
        elif dummyDictAdmin[i]['Model']=="UBIWS":
            sumPaid[1] += (dummyDictAdmin[i]['PaidHours'])
        elif dummyDictAdmin[i]['Model']=="MIGWS":
            sumPaid[2] += (dummyDictAdmin[i]['PaidHours'])        
    for k in range(len(sumPaid)):
        try:
            averagePaid[k]=int(round(sumPaid[k]/modelCounter[k],0))
        except ZeroDivisionError:
            pass
    return averagePaid

def average_income_counter(modelCounter):
    dummyDictAdmin = load_data(pathAdmin)
    sumIncome = [0,0,0]
    averageIncome = [0,0,0]
    for i in dummyDictAdmin:
        if dummyDictAdmin[i]['Model']=="UBI":
            sumIncome[0] += dummyDictAdmin[i]['Income']
        elif dummyDictAdmin[i]['Model']=="UBIWS":
            sumIncome[1] += dummyDictAdmin[i]['Income']
        elif dummyDictAdmin[i]['Model']=="MIGWS":
            sumIncome[2] += dummyDictAdmin[i]['Income']        
    for k in range(len(sumIncome)):
        try:
            averageIncome[k]=int(round(sumIncome[k]/modelCounter[k],0))
        except ZeroDivisionError:
            pass
    return averageIncome