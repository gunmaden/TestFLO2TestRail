from migrator import getSuiteId, getProjectId, getSections, Config
from testrail import *
import jsonpickle as jp

conf = Config()
def auth():
    with open("settings.json", 'r') as file:
        URL = conf.TestRailURL
        login = conf.TestRailLogin
        password = conf.TestRailPassword
        client = APIClient(URL)
        client.user = login
        client.password = password
        return client


client = auth()

projectId = getProjectId(client, conf.TestRailProjectName)
suiteId = getSuiteId(client, projectId, conf.TestRailsSuiteName)

counter = 0
for section in getSections(client, projectId, suiteId):
    if section['parent_id'] is None:
        client.send_post('delete_section/{}'.format(section['id']), data=None)
        counter += 1
        print("Deleted {} template(s)".format(counter))
