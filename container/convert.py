import json
import os
from typing import List
import re

# get REPO_URL from environment

repo = f'https://github.com/{os.getenv("GITHUB_REPOSITORY")}/blob/{os.getenv("GITHUB_SHA")}/'


rules = []

precisions = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "very-high": 4,
}

precisions_r = {
    1: "low",
    2: "medium",
    3: "high",
    4: "very-high",
}

Rule = [float, str, str, str]


def LoadSarif(path) -> dict:
    # open file and convert to json
    try:
        with open(path) as content:
            data = content.read()
            df = json.loads(data)
            return df
    except:
        return None


def resultToMarkdown(result) -> Rule:
    # Format sarif results to markdown
    message = result["message"]["text"]

    # Remove markdown links
    message = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", message)

    location = result["locations"][0]["physicalLocation"]
    rulesIndex = result["rule"]["index"]
    rule = rules[rulesIndex]
    id = rule["id"]
    precision = rule["properties"]["precision"]

    shortDescription = rule["shortDescription"]["text"]
    fullDescription = rule["fullDescription"]["text"]

    if not "security" in rule["properties"]["tags"]:
        return -1, "", "", "", "", "", "", ""

    cvss = rule["properties"]["security-severity"]

    line = "L{}".format(location["region"]["startLine"])
    if "endLine" in location["region"]:
        line = "{}-L{}".format(line, location["region"]["endLine"])
    full_url = "{}{}#{}".format(
        repo, location["artifactLocation"]["uri"], line)
    uri = location["artifactLocation"]["uri"]

    return float(cvss), id, shortDescription, fullDescription, precision, message, uri, full_url


def issueToMd(issue) -> str:
    content = "Title  | File | Precision  \n--------- | --------- | ---------\n"
    end = "</details>"
    start = \
        "<details>" \
        f'<summary>{issue["shortDescription"]}</summary>\n\n' \
        f'**Score:** *{issue["cvss"]}*\n' \
        f'**Definition**: *{issue["fullDescription"]}*\n' \
        f'**ID:** `{issue["id"]}`\n'

    vulns = issue["vulnerabilities"]
    # Sort vulns by precision
    vulns = sorted(vulns, key=lambda x: x[1])
    for vuln in vulns:
        content += "{}|{}|{}\n".format(vuln[0].replace(".", ""),vuln[1],
                                    str.capitalize(precisions_r[vuln[2]]))

    return f"{start} \n {content}\n {end}\n"


def resultsToMd(results, ignore) -> List[str]:
    # Format sarif issues as markdown
    issues = {}
    for result in results:
        cvss, id, shortDescription, fullDescription, precision, message, uri, url = resultToMarkdown(
            result)
        if cvss == -1 or id in ignore or uri in ignore:
            continue

        # add new issue to issues with id as key
        if not id in issues:
            issues[id] = {"cvss": cvss, "id": id, "shortDescription": shortDescription,
                          "fullDescription": fullDescription, "vulnerabilities": []}
        issues[id]["vulnerabilities"].append(
            [message, "[{}]({})".format(uri, url), precisions[precision]])

    output = "# {}\n\n".format("Security issues")

    issues_list = list(issues.values())
    # Sort issues_list by cvss
    issues_list = sorted(issues_list, key=lambda x: x["cvss"], reverse=True)

    # Splits the issues into 3 lists
    cvss_high = []
    cvss_medium = []
    cvss_low = []

    for i in range(len(issues_list)):
        if issues_list[i]["cvss"] < 4:
            cvss_low.append(issues_list[i])
        elif issues_list[i]["cvss"] < 7:
            cvss_medium.append(issues_list[i])
        else:
            cvss_high.append(issues_list[i])

    # Converts the issues_list to markpdown
    high_text = "## High Priority \n"
    medium_text = "## Medium Priority\n"
    low_text = "## Low Priority\n"

    for i in cvss_high:
        high_text += issueToMd(i)
    for i in cvss_medium:
        medium_text += issueToMd(i)
    for i in cvss_low:
        low_text += issueToMd(i)

    # Create markdown for high, medium and low
    if cvss_high:
        output += high_text + "\n\n"
    if cvss_medium:
        output += medium_text + "\n\n"
    if cvss_low:
        output += low_text + "\n\n"

    if len(issues_list) == 0:
        output += "No security issue found, good job!\n"
    return output


def LoadRules(sarif):
    global rules
    rules = sarif["runs"][0]["tool"]["driver"]["rules"]


def sarifToMD(path):
    sarif = LoadSarif(path)
    LoadRules(sarif)
    ignore = []
    try:
        with open(f"{os.getenv('GITHUB_WORKSPACE')}/.sastignore") as content:
            ignore = content.read().split("\n")
    except:
        print("No .sastignore detected")
        

    return(resultsToMd(sarif["runs"][0]["results"], ignore))
