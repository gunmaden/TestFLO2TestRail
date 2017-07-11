from migrator import getSuiteId, getProjectId, getSections
from testrail import *
import jsonpickle as jp


def auth():
    with open("settings.json", 'r') as file:
        URL = jp.decode(file)['TestRailURL']
        login = jp.decode(file)['TestRailLogin']
        password = jp.decode(file)['TestRailPassword']
        client = APIClient(URL)
        client.user = login
        client.password = password
        return client


client = auth()

projectId = getProjectId(client)
suiteId = getSuiteId(client, projectId)

counter = 0
for section in getSections(client, projectId, suiteId):
    if section['parent_id'] is None:
        client.send_post('delete_section/{}'.format(section['id']), data=None)
        counter += 1
        print("Deleted {} template(s)".format(counter))
