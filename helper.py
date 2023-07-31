import colorama
from datetime import datetime
from consts import *
import json
import os

colorama.init()
Fore = colorama.Fore


with open("generator_files/prompt.txt", "r") as f:
    PROMPTTEXT = f.read()

with open("generator_files7template.json", "r") as f:
    PROMPTTEXT = PROMPTTEXT.replace("{doc}", f.read())



def printLogInfo(overallSuccess, possibleErrorPoints, title, depth):
    status = Fore.GREEN + " SUCCESS " + Fore.RESET if \
            overallSuccess \
            else Fore.RED + " FAILURE " + Fore.RESET

    reason = "REASON: " + " ".join(Fore.RED + "F" + Fore.RESET if ep else "S" for ep in possibleErrorPoints) \
        if not overallSuccess else ""

    timestamp = " " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " "

    print(f"{timestamp} {str(depth).rjust(2, '0')} {status} {title.ljust(20, ' ')} {reason}")

def updateReachedDepth(depth):
    try:
        with open("status/maxDepth.txt", "r") as f:
            d = int(f.read())
    except:
        d = 0

    if d < depth:
        with open("status/maxDepth.txt", "w") as f:
            f.write(str(depth))

def parsePrompt(title):
    return PROMPTTEXT.replace("{title}", title)

def conceptExists(conceptName):
    conceptNameFilePart = conceptName.lower().replace(" ", "_") + ".json"
    for filename in os.listdir(CONCEPT_DIR):
        if filename.split("_")[1] == conceptNameFilePart:
            return True
    return False

def conceptToFilePath(conceptName, depth):
    return CONCEPT_DIR + "/" + str(depth).rjust(2, "0") + "_" + conceptName.lower().replace(" ", "_") + ".json"



def saveResponse(response):
    with open(conceptToFilePath(response["title"], response["depth"]), "w") as f:
        json.dump(response, f, indent=4)

def saveErrResponse(responseStr):
    with open("status/errResponses.txt", "a") as f:
        f.write(responseStr + "\n\n")


