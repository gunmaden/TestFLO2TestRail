import requests
from objectpath import *
import jsonpickle as jp
from migrator import *


def auth():
    # login = ""
    # password = ""
    with open("settings.json", 'r') as file:
        login = jp.decode(file)['JiraLogin']
        password = jp.decode(file)['JiraPassword']
        credentials = {
            "os_username": login,
            "os_password": password
        }
        return credentials


def retTemplateT():
    return {
        'TemplateName': '',
        'CaseGroups': []
    }


def retGroupsT():
    return {
        'GroupName': '',
        'Cases': []
    }


def retCaseT():
    return {
        'Name': None,
        'ExpectedResult': "",
        'Steps': ""
    }


###################################################################################################################

req = requests.post("https://jira.parcsis.org/rest/gadget/1.0/login", data=auth())
cookies = None

while cookies is None:
    if req.json()['loginSucceeded']:
        cookies = req.cookies
    elif not req.json()['loginSucceeded']:
        print("Login incorrect! Try again \r\n")
        req = requests.post("https://jira.parcsis.org/rest/gadget/1.0/login", data=auth())
    else:
        print("Shit happens")

issuesReq = {
    'startIndex': 0,
    'jql': 'project = {} and type = "Test Case Template" and status = Active'.format(
        input("Enter project name ( CASEM / CSP / CL / CB): "))
}

headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'x-atlassian-token': 'nocheck'
           }

issues = requests.post("https://jira.parcsis.org/rest/issueNav/1/issueTable", data=issuesReq, cookies=cookies,
                       headers=headers)

templatesIds = issues.json()['issueTable']['issueIds']

counter = 0

for templateId in templatesIds:
    templateContent = requests.get("https://jira.parcsis.org/rest/api/2/issue/{}".format(templateId), cookies=cookies)
    templateCategory = templateContent.json()['fields']['summary']

    fields = templateContent.json()['fields']

    actionColumnNumber = Tree(templateContent.json()).execute("$..header..*[@.name is 'Action']")
    expectedResultColumnNumber = Tree(templateContent.json()).execute(
        "$..header..*[@.name is 'Expected result']")
    cN = 0
    erN = 0
    for el in actionColumnNumber:
        cN = el['number']

    for el in expectedResultColumnNumber:
        erN = el['number']

    cTemplate = retTemplateT()
    cTemplate['TemplateName'] = templateCategory
    groupNames = Tree(fields).execute("$..groupName")
    groups = set(list(groupNames))
    if len(groups) == 0:
        print("Warning: all steps in template without groups will be grouped by same name as template")
        groups.add(templateCategory)
    print("Start migrating template: {}".format(templateCategory))
    for gr in groups:
        cGroup = retGroupsT()
        cGroup['GroupName'] = gr

        steps = Tree(templateContent.json()).execute("$..columns..*[@.groupName is '{}']".format(gr))
        steps = Tree(steps).execute("$..*[@.number is {}]".format(cN))

        expRes = Tree(templateContent.json()).execute("$..columns..*[@.groupName is '{}']".format(gr))
        expRes = Tree(expRes).execute("$..*[@.number is {}]".format(erN))

        stepsL = []
        expResL = []
        for step in steps:
            stepsL.append(step['value'])
        for res in expRes:
            expResL.append(res['value'])

        for i in range(0, len(stepsL)):
            case = retCaseT()
            case['Name'] = "Case #{}".format(i + 1)
            case['ExpectedResult'] = expResL[i]
            case['Steps'] = stepsL[i]
            cGroup['Cases'].append(case)

        cTemplate['CaseGroups'].append(cGroup)
    migrateTemplate(cTemplate)
    print("Template {} Migrated ".format(templateCategory))
    counter += 1
    print("Estimated templates: {}".format(len(templatesIds) - counter), '\n\n')
