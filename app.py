from flask import Flask, render_template, url_for, session, redirect, request
import random
import string
import os
import json
from datetime import date, datetime
from dotenv import load_dotenv
import admin


class Tasks():
    id = 0
    content = ""
    correctAnswer = ""
    submittedAnswer = ""
    attempt = 0
    timeStart = datetime.utcnow().isoformat()
    timeSubmit = datetime.utcnow().isoformat()
    income = 0


class Comics():
    id=0
    link=""
    timeStart = datetime.utcnow().isoformat()
    timeSubmit = datetime.utcnow().isoformat()


def id_generator():
    return "".join([random.choice(string.ascii_letters
            + string.digits) for n in range(10)])


def load_data(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.loads(f.read())


def save_json(path, data):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=2))

def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_if_not_exists(path, default_content):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(json.dumps(default_content))
            f.close()

def income_calculator(model, hours, G, wage, tax, subsidy):
    if model == 'UBI':
        payoff = G + 4*hours*wage*(1-tax)
    elif model == 'UBIWS':
        if 4 * hours * wage * (1 + subsidy) < G/2:
            payoff = G/2 + 4 * hours * wage * (1 + subsidy)
        else:
            payoff = G/2 + 4 * wage *hours * (1 + subsidy - tax)
    elif model == 'MIGWS':
        if 4 * hours * wage * (1 + subsidy) < G/2:
            payoff = G/2
        else:
            payoff = 4 * hours* wage * (1 + subsidy - tax)
    return int(round(payoff,0))    


app = Flask(__name__)
load_dotenv()
app.secret_key=os.getenv('TOKEN')
wage = 22.5
hoursForWork = 40
threshold = 1200
tax = 0.25
subsidy = 0.1

pathMaths = os.path.join(os.getcwd(), 'maths_tasks.json')
pathComics = os.path.join(os.getcwd(), 'comics.json')
pathInfo = os.path.join(os.getcwd(), 'info.json')
pathDataFolder = os.path.join(os.getcwd(), 'data')

tasksDB = load_data(pathMaths)
tasksKeys = list(tasksDB.keys())
tasksValues = list(tasksDB.values())

comicsDB=load_data(pathComics)

currentTask = Tasks()
currentComics = Comics()

@app.route('/')
def index():
    if 'Subject' not in session:
        session['Subject'] = id_generator()
        session['StartTime']=datetime.utcnow().isoformat()
    return render_template('index.html')
    
@app.route('/model')
def model_distributor():
    if 'Model' not in session:
        infoDict = load_data(pathInfo)
        if 'Subjects' not in infoDict:
            infoDict['Subjects'] = 1
        else: 
            infoDict['Subjects'] += 1
        session['SubjectNumber']=infoDict['Subjects']
        if "IDlist" not in infoDict:
            infoDict['IDlist'] = [session['Subject']]
        else:
            infoDict['IDlist'].append(session['Subject'])
        save_json(pathInfo, infoDict)
        session['ModelTime']=datetime.utcnow().isoformat()
        session['ModelReturn'] = 0
        if (infoDict['Subjects'] + 2) % 3 == 0:
            session['Model']="UBI"
        elif (infoDict['Subjects']+ 1) % 3 == 0:
            session['Model']="UBIWS"
        else: session['Model']="MIGWS"

        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        create_dir_if_not_exists(pathDataFolder)
        create_if_not_exists(pathData, {})
        dummyDict = load_data(pathData)
        dummyDict['ID']=session['Subject']
        dummyDict['SubjectNumber']=session['SubjectNumber']
        dummyDict['Model']=session['Model']
        dummyDict['ModelTime']=session['ModelTime']
        save_json(pathData, dummyDict)

    else:
        session['ModelReturn'] += 1
        session['ModelReturnTime'] = datetime.utcnow().isoformat()
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['ModelReturn']=session['ModelReturn']
        dummyDict['ModelReturnTime']=session['ModelReturnTime'] 
        save_json(pathData,dummyDict)
    
    if session['Model'] == "UBI":
        return render_template('introduction1.html', wage=wage)
    elif session['Model'] == "UBIWS":
        return render_template('introduction2.html', wage=wage)
    elif session['Model'] == "MIGWS":
        return render_template('introduction3.html', wage=wage)

@app.route('/production_intro')
def production_intro():
    if 'ProductionIntroTime' not in session:
        session['ProductionIntroTime']=datetime.utcnow().isoformat()
        session['ProductionIntroReturn'] = 0
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['ProductionIntroTime']=session['ProductionIntroTime']
        save_json(pathData,dummyDict)
    else:
        session['ProductionIntroReturn'] += 1
        session['ProductionIntroReturnTime'] = datetime.utcnow().isoformat()
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['ProductionIntroReturn']=session['ProductionIntroReturn']
        dummyDict['ProductionIntroReturnTime']=session['ProductionIntroReturnTime']
        save_json(pathData, dummyDict)      
    return render_template('production_intro.html')

@app.route('/maths', methods=['POST', 'GET'])
def maths():
    if 'Points' not in session:
        session['Points'] = hoursForWork
        session['CurrentTask']=tasksKeys[0]
        session['CurrentAnswer']=tasksValues[0]
        session['PaidHours']= 0
        session['Switched'] = 0
        session['SwitchedAtTask']=[]
        session['SwitchedAtIncome']=[]
        session['SwitchedAtHours']=[]
        session['FirstChoice'] = 'Maths'
        session['MathsStart']=datetime.utcnow().isoformat()
        currentTask.id=0
        currentTask.content = tasksKeys[0]
        currentTask.correctAnswer = tasksValues[0]
        currentTask.income=income_calculator(session['Model'],session['PaidHours'],threshold,wage,tax,subsidy)
        session['Income']=currentTask.income
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['FirstChoice']=session['FirstChoice']
        dummyDict['MathsStart']=session['MathsStart']
        save_json(pathData,dummyDict)
        # session['Attempt'][currentTask.id]=1
        # session['SwitchedToMaths']=0
        

    elif 'Points' in session and session['Points'] <= 0:
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        session['FinishProductionTime']=datetime.utcnow().isoformat()
        dummyDict=load_data(pathData)
        dummyDict['FinishProductionTime']=session['FinishProductionTime']
        dummyDict['UnpaidHours']=hoursForWork-session['PaidHours']
        dummyDict['PaidHours']=session['PaidHours']
        dummyDict['UnpaidHours']=hoursForWork-session['PaidHours']
        save_json(pathData,dummyDict)
        return redirect('/results')

    elif 'Points' in session and session['Points'] <= hoursForWork:
        # if 'PaidHours' not in session:
        #     session['PaidHours']=0
        #     currentTask.income=income_calculator(session['Model'],session['PaidHours'],threshold,wage,tax,subsidy)
            # session['Attempt'][str(currentTask.id)] = 1
            # session['SwitchedToMaths'] = 1
            # session['SwitchToMathsTime']=datetime.utcnow().isoformat()
        session['CurrentTask']=tasksKeys[session['PaidHours']]
        session['CurrentAnswer']=tasksValues[session['PaidHours']]
        # currentTask.id=hoursForWork-session['Points']
        currentTask.id=session['PaidHours']
        currentTask.income=income_calculator(session['Model'],session['PaidHours'],threshold,wage,tax,subsidy)
        session['Income']=currentTask.income
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['Income']=session['Income']
        save_json(pathData,dummyDict)
        currentTask.content = session['CurrentTask']
        currentTask.correctAnswer = session['CurrentAnswer']
        
    else: 
        
        return 'Unknown Error! Sorry for that..'
    return render_template('maths.html', points=session['Points'], task=currentTask, income=session['Income'], paid=session['PaidHours'], unpaid=hoursForWork-session['Points']-session['PaidHours'])


@app.route('/check/<int:id>', methods=['POST'])
def check(id):
    taskForCheck = request.form['answerGiven']
    if taskForCheck == session['CurrentAnswer']:
        session['Points'] -= 1
        session['PaidHours'] += 1
 
        return redirect ('/maths')
    elif taskForCheck != session['CurrentAnswer']:
        # session['Attempt'][f'{currentTask.id+1}'] += 1
        return redirect('/maths')
    else:
        return "Error that I wasn't waiting for"


@app.route('/comics', methods = ['POST', 'GET'])
def comics():
    if request.method == 'POST':
        if 'Points' in session and session['Points'] <= 1:
            pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
            dummyDict=load_data(pathData)
            dummyDict['PaidHours']=session['PaidHours']
            dummyDict['UnpaidHours']=hoursForWork-session['PaidHours']
            save_json(pathData,dummyDict)
            return redirect('/results')
        elif 'Points' in session and session['Points'] <= hoursForWork:
            # if 'PaidHours' in session:
                # session['Switched'] += 1
                # session['SwitchedToComicsTime'] =datetime.utcnow().isoformat()
            session['Points'] -= 1
            currentComics.id=hoursForWork-session['Points']
            currentComics.link = comicsDB[currentComics.id]
    else:
        if 'Points' not in session:
            session['Points']=hoursForWork
            session['PaidHours']=0
            session['Income']=income_calculator(session['Model'],session['PaidHours'],threshold,wage,tax,subsidy)
            session['Switched']=0
            session['SwitchedAtTask']=[]
            session['SwitchedAtHours']=[]
            session['SwitchedAtIncome']=[]
            session['FirstChoice'] = 'Comics'
            currentComics.id=0
            currentComics.link=comicsDB[0]
            session['ComicsStart'] = datetime.utcnow().isoformat()
            pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
            dummyDict=load_data(pathData)
            dummyDict['FirstChoice']=session['FirstChoice']
            dummyDict['ComicsStart']=session['ComicsStart']
            save_json(pathData, dummyDict)
        elif 'Points' in session and session['Points'] <= 1:
            session['FinishProductionTime']=datetime.utcnow().isoformat()
            pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
            dummyDict=load_data(pathData)
            dummyDict['PaidHours']=session['PaidHours']
            dummyDict['FinishProductionTime']=session['FinishProductionTime']
            dummyDict['UnpaidHours']=hoursForWork-session['PaidHours']
            save_json(pathData,dummyDict)            
            return redirect('/results')
        elif 'Points' in session and session['Points'] <= hoursForWork:
            currentComics.id=hoursForWork-session['Points']
            currentComics.link = comicsDB[currentComics.id]
            currentComics.timeStart = datetime.utcnow().isoformat()
    return render_template('comics.html', points=session['Points'], link=currentComics.link, income=session['Income'], paid=session['PaidHours'], unpaid=hoursForWork-session['Points']-session['PaidHours'])

@app.route('/switch', methods=['POST'])
def switcher():
    if request.form['Switch'] =='FromMaths':
        session['Switched'] += 1
        # session['SwitchedAtTask'].append(session['PaidHours'])
        session['SwitchedAtIncome'].append(session['Income'])
        session['SwitchedAtHours'].append(session['PaidHours'])
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['Switched']= session['Switched']
        # dummyDict['SwitchedAtTask']=session['SwitchedAtTask']
        dummyDict['SwitchedAtIncome']=session['SwitchedAtIncome']
        dummyDict['SwitchedAtHours']=session['SwitchedAtHours']
        save_json(pathData, dummyDict)
        return redirect('/comics')
    elif request.form['Switch'] == 'FromComics':
        session['Switched'] += 1
        # session['SwitchedAtTask'].append(hoursForWork-session['Points'])
        session['SwitchedAtIncome'].append(session['Income'])
        session['SwitchedAtHours'].append(session['PaidHours'])
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        dummyDict=load_data(pathData)
        dummyDict['Switched']= session['Switched']
        # dummyDict['SwitchedAtTask']=session['SwitchedAtTask']
        dummyDict['SwitchedAtIncome']=session['SwitchedAtIncome']
        dummyDict['SwitchedAtHours']=session['SwitchedAtHours']
        save_json(pathData, dummyDict)
        return redirect('/maths')

@app.route('/results')
def results():
    pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
    dummyDict=load_data(pathData)
    dummyDict['Income']= session['Income']
    save_json(pathData, dummyDict)    
    return render_template('results.html', paid=session['PaidHours'], unpaid=hoursForWork-session['PaidHours'], income=session["Income"])

@app.route('/questionnaire')
def questionnaire():
    if session['Model']=="UBI":
        return render_template('questionnaire1.html')
    elif session['Model']=='UBIWS':
        return render_template('questionnaire2.html')
    elif session['Model']=='MIGWS':
        return render_template('questionnaire3.html')

@app.route('/end', methods=['POST', 'GET'])
def end():
    if request.method=='POST':
        pathData=os.path.join(pathDataFolder, f"{session['Subject']}.json")
        questionnaireQuestions = list(request.form.keys())
        questionnaireAnswers = list(request.form.values())
        questionnaireDict = dict(zip(questionnaireQuestions, questionnaireAnswers))
        questionnaireDict['Q4'] = request.form.getlist('Q4')
        questionnaireDict['Q6'] = request.form.getlist('Q6')
        dummyDict = load_data(pathData)
        dummyDict.update(questionnaireDict)
        dummyDict['FinishTime']=datetime.utcnow().isoformat()
        save_json(pathData,dummyDict)
    return render_template('end.html')

@app.route('/controlpanel')
def controlpanel():
    counter=admin.model_counter()
    return render_template('controlpanel.html', 
                            subjects=admin.subject_counter(),
                            finished=admin.finished_subject_counter_and_saver(),
                            model=counter,
                            averagePaid=admin.average_income_counter(counter),
                            averageIncome=admin.average_income_counter(counter)
                            )

if __name__ == "__main__":
    app.run(debug=True)

