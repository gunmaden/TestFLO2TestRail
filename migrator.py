import jsonpickle as jp
from objectpath import *
from testrail import *


################## RETURN TEMPLATES ###################

def retProjL(prL):
    return {
        'Projects': prL
    }


def retSuitesL(sL):
    return {
        'Suites': sL
    }


def retSectionBodyT():
    return {
        'name': "",
        'suite_id': ""
    }


def retSubsectionBodyT():
    return {
        'name': "",
        'suite_id': "",
        'parent_id': ""
    }


#######################################################


################## MAIN FUNCTIONS #####################




class testCase:
    def __init__(self, title, steps, expected):
        self.title = title
        self.template_id = 1
        self.type_id = 7
        self.priority_id = 2
        self.custom_steps = steps
        self.custom_expected = expected

    def create(self, client, sectionId):
        case = jp.decode(jp.encode(self, unpicklable=False))
        return client.send_post('add_case/{}'.format(sectionId), data=case)


def readConfig():
    with open("settings.json", 'r') as f:
        file = f.read()
        return jp.decode(file)


class Config():

    def __init__(self):
        self.JiraLogin = readConfig()["JiraLogin"],
        self.JiraPassword = readConfig()["JiraPassword"],
        self.JiraProjectName = readConfig()["JiraProjectName"]
        self.TestRailURL = readConfig()["TestRailURL"]
        self.TestRailLogin = readConfig()["TestRailLogin"]
        self.TestRailPassword = readConfig()["TestRailPassword"]
        self.TestRailProjectName = readConfig()["TestRailProjectName"]
        self.TestRailsSuiteName = readConfig()["TestRailsSuiteName"]
        self.CaseTypes = readConfig()["CaseTypes"]

    def __repr__(self):
        jp.decode(jp.encode(self, unpicklable=False))

conf = Config()

def auth():
    URL = conf.TestRailURL
    login = conf.TestRailLogin
    password = conf.TestRailPassword
    client = APIClient(URL)
    client.user = login
    client.password = password
    return client


def addSection(client, section, projectId):
    return client.send_post('add_section/{}'.format(projectId), data=section)


def getSections(client, projectId, suiteId):
    return client.send_get('get_sections/{}&suite_id={}'.format(projectId, suiteId))


def getProjects(client):
    return client.send_get('get_projects')


def getProjectId(client, projectName):
    return Tree(retProjL(getProjects(client))) \
        .execute("$..Projects..*[@.name is '{}'][0]".format(projectName))['id']


def getSuites(client, projectId):
    return client.send_get('get_suites/{}'.format(projectId))


def getSuiteId(client, projectId, suiteName):
    return Tree(retSuitesL(getSuites(client, projectId))) \
        .execute("$..Suites..*[@.name is '{}'][0]".format(suiteName))['id']


def migrateTemplate(template):
    client = auth()

    projectId = getProjectId(client)
    suiteId = getSuiteId(client, projectId)
    groupList = template['CaseGroups']

    sectionBody = retSectionBodyT()
    sectionBody['name'] = template['TemplateName']
    sectionBody['suite_id'] = suiteId

    section = addSection(client, sectionBody, projectId)

    for group in groupList:

        subSectionBody = retSubsectionBodyT()
        subSectionBody['name'] = group['GroupName'] or "empty"
        subSectionBody['suite_id'] = suiteId
        subSectionBody['parent_id'] = section['id']

        subSection = addSection(client, subSectionBody, projectId)

        counter = 0
        for case in group['Cases']:
            counter += 1
            testCase(
                "Case #{}".format(counter),
                case['Steps'],
                case['ExpectedResult']).create(
                client,
                subSection['id']
            )
