import json
import os
from consts import *

def findAllUnconvertedConceptFiles():
    conceptFileList = []
    for filename in os.listdir(CONCEPT_DIR):
        file_path = os.path.join(CONCEPT_DIR, filename)
        if not os.path.isfile(file_path) or not filename.endswith(".json"): continue
        if os.path.exists(os.path.join(MDFILE_DIR, filename.replace(".json", ".md"))): continue
        
        conceptFileList.append(file_path)

    return conceptFileList


def asWikiLinkList(lst):
    return "\n".join(f"- [[{item}]]" for item in lst)

def asTagList(lst):
    return "\n".join(f"- #{item.replace(' ', '_')}" for item in lst)

def convertToMdFileFromFile(sourceLoc, targetDir=MDFILE_DIR, template=template):
    with open(sourceLoc, "r") as f:
        content = json.load(f)

    fileName = content["title"] + ".md"
    mdstr = convertToMdStringFromJson(content, template)
    saveAsMdFile(mdstr, fileName, targetDir)

def convertToMdFileFromJson(content, targetDir=MDFILE_DIR, template=template):
    fileName = content["title"] + ".md"
    mdstr = convertToMdStringFromJson(content, template)
    saveAsMdFile(mdstr, fileName, targetDir)

def convertToMdStringFromJson(content, template=template):
    return template \
        .replace("{def}", content["definition"]) \
        .replace("{ref}", asWikiLinkList(content["child_concepts"])) \
        .replace("{fields}", asTagList(content["concept_fields"])) \
        .replace("{knownsince}", str(content["known_since"]))

def saveAsMdFile(mdstr, fileName, loc=MDFILE_DIR):
    with open(os.path.join(loc, fileName), "w") as f:
        f.write(mdstr)


if __name__ == "__main__":
    for conceptFileLoc in findAllUnconvertedConceptFiles():
        convertToMdFileFromFile(conceptFileLoc, MDFILE_DIR)


