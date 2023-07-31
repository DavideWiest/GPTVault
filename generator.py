import os
import openai
from colorama import Fore
import json
import sys
from helper import *
from consts import *
from converter import convertToMdFileFromJson

openai.api_key = os.getenv("OPENAI_API_KEY")



def startBFProcessFromLayer(depthLimit, depthTarget=-1, convertToMd=False):
    if depthTarget == -1:
        with open("status/maxDepth.txt") as f:
            depthTarget = int(f.read())-1

    conceptsToFind = []
    for filename in os.listdir(CONCEPT_DIR):
        file_path = os.path.join(CONCEPT_DIR, filename)
        if not os.path.isfile(file_path) or not filename.endswith(".json"): continue
        if int(filename.split("_")[0]) != depthTarget: continue
        
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
                child_concepts = data.get("child_concepts", [])
                conceptsToFind += child_concepts
            except json.JSONDecodeError as e:
                print(f"Error loading JSON in file '{file_path}': {e}")

    gatherKnowledgeBF(inputConcepts=conceptsToFind, depth=depthTarget+1, depthLimit=depthLimit, convertToMd=convertToMd)


def gatherKnowledgeDF(concept, depth=0, depthLimit=15, convertToMd=False):
    # depth first search

    if conceptExists(concept): return

    response = conceptNode(concept, depth=depth, convertToMd=convertToMd)
    if response == None: return
    
    response["depth"] = depth
    saveResponse(response)

    if depthLimit <= depth-1:
        print(Fore.GREEN + f"End Program because depthLimit of {depthLimit} has been reached." + Fore.RESET)
        sys.exit(0)

    updateReachedDepth(depth)

    for childConcept in response["child_concepts"]:
        gatherKnowledgeDF(childConcept, depth=depth+1)


def gatherKnowledgeBF(inputConcepts, depth=0, depthLimit=15, convertToMd=False):
    # breadth first search

    queue = [(concept, depth) for concept in inputConcepts]

    while queue:
        concept, depth = queue.pop(0)
        if conceptExists(concept):
            continue

        response = conceptNode(concept, depth=depth, convertToMd=convertToMd)
        if response == None: continue

        response["depth"] = depth
        saveResponse(response)

        if depthLimit <= depth:
            print(Fore.GREEN + f"End Program because depthLimit of {depthLimit} has been reached." + Fore.RESET)
            sys.exit(0)

        updateReachedDepth(depth)

        for childConcept in response["child_concepts"]:
            queue.append((childConcept, depth + 1))  # Enqueue child concepts with an incremented depth


def conceptNode(title, logInfo=True, max_tokens=MAX_TOKENS_BASE, retries=0, depth=0, convertToMd=False):
    responseCorrect = True
    messageWhole = True
    messageParsed = True

    try:
        response = makeResponse(parsePrompt(title), max_tokens)
        responseStr = response["choices"][0]["message"]["content"]
    except:
        responseCorrect = False
    
    if responseCorrect:
        messageWhole = response["choices"][0]["finish_reason"] == "stop"

    try:
        responseJson = json.loads(responseStr)
    except:
        messageParsed = False

    if messageParsed:
        if not all(key in list(responseJson.keys()) for key in templateKeys):
            messageParsed = False

    possibleErrorPoints = [responseCorrect, messageWhole, messageParsed]
    overallSuccess = all(possibleErrorPoints)
    
    if logInfo:
        printLogInfo(overallSuccess, possibleErrorPoints, title, depth)

    if not overallSuccess:
        if responseCorrect:
            saveErrResponse(responseStr)
        return handledErrorResponse(responseCorrect, messageParsed, messageWhole, title, logInfo, max_tokens, retries, convertToMd)
    else:
        convertToMdFileFromJson(responseJson)

    return responseJson

def handledErrorResponse(responseCorrect, messageParsed, messageWhole, title, logInfo, max_tokens, retries, convertToMd):
    if retries >= 10:
        if not responseCorrect or not messageParsed:
            print(Fore.RED + "End Program due to apparently repeating error." + Fore.RESET)
            sys.exit(0)
        else:
            print(Fore.RED + "Skipping node due to apparently repeating error." + Fore.RESET)
            with open("status/skippedNodes.txt", "a") as f:
                f.write(title + "\n")
            return 
    
    if not messageWhole:
        return conceptNode(title=title, logInfo=logInfo, max_tokens=max_tokens+50, retries=retries+1, convertToMd=convertToMd)
    return conceptNode(title=title, logInfo=logInfo, max_tokens=max_tokens, retries=retries+1, convertToMd=convertToMd)

def makeResponse(prompt, max_tokens):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_ROLE
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

if __name__ == "__main__":
    command = input("Usage Type: (new/fromlayer)")
    if command == "new":
        startingFields = [
            f.strip() for f in input("Starting topic(s) (separated by comma): ").split(",")
        ]

        gatherKnowledgeBF(startingFields, depthLimit=int(input("Depth Limit (up to 12 is recommended): ")), convertToMd=True)

    elif command == "fromlayer":
        startBFProcessFromLayer(depthLimit=int(input("Depth Limit (up to 12 is recommended): ")), depthTarget=int(input("Depth target (-1 for auto eval): ")), convertToMd=True)
    
    else:
        print(Fore.RED + "Invalid option, try again by restarting the program." + Fore.RESET)


