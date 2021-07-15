import random 
import os
import json


def save_json(path, data):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=2))

# what stays here in brackets goes at respective places to the function
def tasks_generator(range11, range12, range21, range22, tasksAmount):
    target_dict = {}
# here are two lists of random numbers created in specified range
    first_number_list = [random.randint(range11, range12) for _ in range(tasksAmount)]
    second_number_list = [random.randint(range21, range22) for k in range(tasksAmount)]
# here are answers generated (in our case - multiplication)
    answers_list = [first_number_list[i]*second_number_list[i] for i in range(tasksAmount)]
# here a variable is created which stores all the tasks in string form and the answers. We will use them for the website
    for k in range(tasksAmount):
        target_dict["".join(str(first_number_list[k]) + " * " + str(second_number_list[k]))] = str(answers_list[k])
    return target_dict

# here are the parameters for the task generator function (change here)
range11 = 11
range12 = 19
range21 = 21
range22 = 29
tasksAmount = 40

# this is a dummy variable of type "dict"
dictForSave = {}

# this checks that we have necessary amount of unique tasks 
while True:
    if len(dictForSave) != tasksAmount:
        dictForSave = tasks_generator(range11, range12, range21, range22, tasksAmount)
    else:
        break

path = os.path.join(os.getcwd(), "maths_tasks.json")
save_json(path, dictForSave)
print("file maths.json generated successfully!")