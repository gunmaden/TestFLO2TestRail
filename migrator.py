import jsonpickle as jp

from testrail import *


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


def auth():
     with open("settings.json", 'r') as file:
        URL = jp.decode(file)['TestRailURL']
        login = jp.decode(file)['TestRailLogin']
        password = jp.decode(file)['TestRailPassword']
        client = APIClient(URL)
        client.user = login
        client.password = password
        return client


def addSection(client, section, projectId):
    return client.send_post('add_section/{}'.format(projectId), data=section)


def getSections(client, projectId, suiteId):
    return client.send_get('get_sections/{}&suite_id={}'.format(projectId, suiteId))


def getProjectId(client):
    return client.send_get('get_projects')[0]['id']


def getSuiteId(client, projectId):
    return client.send_get('get_suites/{}'.format(projectId))[0]['id']


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
