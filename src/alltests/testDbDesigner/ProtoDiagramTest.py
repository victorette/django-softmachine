# -*- encoding: UTF-8 -*-

from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpRequest
from dbDesigner.protoDiagram import getEntitiesJSONDiagram, synchDiagramFromDB, getElementsDiagramFromSelectedTables, synchDBFromDiagram, getDefaultDiagram
from dbDesigner.protoDiagramEntity import listDiagrams, openDiagram, createDiagram, saveDiagram, deleteDiagram
from dbDesigner.service.diagramService import addOrUpdateConnector
from prototype.models import Relationship
from alltests.testPrototype.testmodels.TestUtilities import createTestDiagram, createTestEntity, createTestRelationship, createTestProperty, createTestProject
from requests import Request
from django.contrib.auth import authenticate
import json, uuid, unicodedata

def CreateBasicRequest():
    request = HttpRequest()
    request.method = 'POST'
    request.POST['login'] = 'adube'
    request.POST['password'] = '123'
    request.user = authenticate(username=request.POST['login'], password=request.POST['password'])
    request.POST['projectID'] = 1

    return request

def CreatePreparedRequest():
    data = '[{"id":"465bf0b2-a50f-f6cb-fdf0-0cbf142d239b","tableName":"Document"}]'
    req = Request('GET', 'http://url', headers=None, files=None, data=data, params="id=1", auth=None, cookies=None, hooks=None)
    return req.prepare()

def CreatePreparedAuthRequest():

    factory = RequestFactory()
    attributes = [{"text":"new attribute0", 
                   "id":"b3177ad1-b220-805e-e748-be12434e578d", 
                   "datatype":"string", 
                   "pk":True, 
                   "fk":False, 
                   "isRequired":True, 
                   "isNullable":False},
                  {
                    "text": "blubber",
                    "id": "49be7d78-4dcf-38ab-3733-b4108701fce4",
                    "datatype": "int",
                    "pk": True,
                    "fk": False,
                    "isNullable": False,
                    "isRequired": True
                  }]
    table = {"type":"dbModel.shape.DBTable", 
             "id":"10eeb1fa-ca72-84d1-82a3-d9cbf75715b0", 
             "x":20, 
             "y":20, 
             "width":99, 
             "height":57.84375, 
             "userData":{}, 
             "cssClass":"DBTable", 
             "bgColor":"#DBDDDE", 
             "color":"#D7D7D7", 
             "stroke":1, 
             "alpha":1, 
             "radius":3, 
             "tableName":"TableName10", 
             "tablePorts":[], 
             "attributes":attributes}
    connectorName = 'Connection t1 t2'
    connector = {
                "type": "dbModel.shape.TableConnection",
                "id": "f8735797-cf1d-8431-d891-c2d10f0a67be",
                "name": connectorName,
                "userData": {"isPrimary":True, "useDecorators": False},
                "cssClass": "draw2d_Connection",
                "stroke": 2,
                "color": "#5BCAFF",
                "policy": "draw2d.policy.line.LineSelectionFeedbackPolicy",
                "router": "draw2d.layout.connection.InteractiveManhattanConnectionRouter",
                "source": {
                  "node": "10eeb1fa-ca72-84d1-82a3-d9cbf75715b0",
                  "port": "output1"
                },
                "target": {
                  "node": "465bf0b2-a50f-f6cb-fdf0-0cbf142d239b",
                  "port": "input0"
                }
              }
    data = json.dumps([table, connector])
    auth = authenticate(username='adube', password='123')

    request = factory.request()
    request._body = data
    request._get = {"projectID":1, "diagramID":1}
    request.user = auth

    return request

def CreatePreparedExistentEntityAuthRequest():

    factory = RequestFactory()
    data = '[{"type":"dbModel.shape.DBTable","id":"465bf0b2-a50f-f6cb-fdf0-0cbf142d239b","x":20,"y":20,"width":99,"height":57.84375,"userData":{},"cssClass":"DBTable","bgColor":"#DBDDDE","color":"#D7D7D7","stroke":1,"alpha":1,"radius":3,"tableName":"TableName10","tablePorts":[],"attributes":[{"text":"new attribute0","id":"b3177ad1-b220-805e-e748-be12434e578d","datatype":"string","pk":true,"fk":false,"isRequired":true,"isNullable":false}]}]'
    auth = authenticate(username='adube', password='123')

    request = factory.request()
    request._body = data
    request._get = {"projectID":1, "diagramID":1}
    request.user = auth

    return request

def CreatePreparedAuthPostRequest():

    factory = RequestFactory()
    auth = authenticate(username='adube', password='123')

    request = factory.post("/protoLib/createDiagram", {u'diagrams': [u'{"projectID":1,"id":"1","code":"test","smUUID":""}']})
    request.user = auth

    return request

class ProtoDiagramTest(TestCase):

    def setUp(self):
        self.diagram = createTestDiagram()
        self.property = createTestProperty()
        self.basic_request = CreateBasicRequest()
        self.auth_request = CreatePreparedAuthRequest()
        self.auth_request_existent_entity = CreatePreparedExistentEntityAuthRequest()

    def tearDown(self):
        self.diagram.delete()
        self.property.delete()

    def test_verifying_diagram_entities_in_database(self):
        response = json.loads(getEntitiesJSONDiagram(self.basic_request).content)
        self.assertTrue(response['success'])

    def test_synchDiagramFromDB(self):
        response = json.loads(synchDiagramFromDB(self.basic_request).content)
        self.assertTrue(response['success'])

    def test_synchDBFromDiagram(self):
        response = json.loads(synchDBFromDiagram(self.auth_request).content)
        self.assertTrue(response['success'])

    def test_synchDBFromDiagramWhenEntityExistsThenReturnSuccess(self):
        response = json.loads(synchDBFromDiagram(self.auth_request_existent_entity).content)
        self.assertTrue(response['success'])

    def test_getDefaultDiagram(self):
        response = json.loads(getDefaultDiagram(self.auth_request).content)
        self.assertTrue(response['success'])

class ProtoCreateDiagramTest(TestCase):
    def setUp(self):
        self.auth_request = CreatePreparedAuthRequest()
    
    def test_getDefaultDiagramThenCreateANewOne(self):
        self.project = createTestProject()
        response = json.loads(getDefaultDiagram(self.auth_request).content)
        self.project.delete()
        self.assertTrue(response['success'])
        
    def test_getDefaultDiagramThenThrowException(self):
        response = json.loads(getDefaultDiagram(self.auth_request).content)
        self.assertFalse(response['success'])
        
class ProtoDiagramEntityTest(TestCase):
    def setUp(self):
        self.entity = createTestEntity()
        self.diagram = createTestDiagram()
        self.basic_request = CreateBasicRequest()
        self.prepped_request = CreatePreparedRequest()
        self.auth_request = CreatePreparedAuthRequest()
        self.auth_request_existent_entity = CreatePreparedExistentEntityAuthRequest()

        self.testRelationShip = createTestRelationship()

    def tearDown(self):
        self.entity.delete()
        self.diagram.delete()

    def test_getEntitiesJSONDiagram_thenReturnEntity(self):
        response = json.loads(getEntitiesJSONDiagram(self.basic_request).content)
        tab = response['tables'][0]
        tabName = unicodedata.normalize('NFKD', tab['tableName']).encode('ascii', 'ignore')
        self.assertEqual(self.entity.code, tabName)

    def test_getElementsDiagramFromSelectedTables(self):
        response = json.loads(getElementsDiagramFromSelectedTables(self.prepped_request).content)
        smUUID = uuid.UUID(response['tables'][0]['id']).hex
        self.assertEqual(self.entity.smUUID, smUUID)

    def test_listDiagrams(self):
        response = json.loads(listDiagrams(self.auth_request).content)
        self.assertTrue(response['success'])

    def test_openDiagram(self):
        response = json.loads(openDiagram(self.auth_request).content)
        self.assertTrue(response['success'])

    def test_saveDiagram(self):
        response = json.loads(saveDiagram(self.auth_request_existent_entity).content)
        self.assertTrue(response['success'])

    def test_createDiagram(self):
        request = CreatePreparedAuthPostRequest()
        response = json.loads(createDiagram(request).content)
        self.assertTrue(response['success'])

    def test_deleteDiagram(self):
        request = CreatePreparedAuthPostRequest()
        response = json.loads(deleteDiagram(request).content)
        self.assertTrue(response['success'])

    def test_addOrUpdateConnectorThenSaveChanges(self):
        connectorName = 'Connection t1 t2'
        element = {
                    "type": "dbModel.shape.TableConnection",
                    "id": "f8735797-cf1d-8431-d891-c2d10f0a67be",
                    "name": connectorName,
                    "userData": {"isPrimary":True, "useDecorators": False},
                    "cssClass": "draw2d_Connection",
                    "stroke": 2,
                    "color": "#5BCAFF",
                    "policy": "draw2d.policy.line.LineSelectionFeedbackPolicy",
                    "router": "draw2d.layout.connection.InteractiveManhattanConnectionRouter",
                    "source": {
                      "node": "3253ff2a-a920-09d5-f033-ca759a778e19",
                      "port": "output1"
                    },
                    "target": {
                      "node": "2810494b-931f-da59-fd9d-6deba4385fe0",
                      "port": "input0"
                    }
                  }
        elementUUID = 'f8735797cf1d8431d891c2d10f0a67be'
        addOrUpdateConnector(element, elementUUID, self.entity, self.entity)
        connector = Relationship.objects.get(smUUID=elementUUID)
        self.assertTrue(connector.code == connectorName)

    def test_addOrUpdateConnectorThenCreateANewOne(self):
        connectorName = 'Connection t1 t2'
        element = {
                    "type": "dbModel.shape.TableConnection",
                    "id": "f9735797-cf1d-8431-d891-c2d10f0a67be",
                    "name": connectorName,
                    "userData": {"isPrimary":True, "useDecorators": False},
                    "cssClass": "draw2d_Connection",
                    "stroke": 2,
                    "color": "#5BCAFF",
                    "policy": "draw2d.policy.line.LineSelectionFeedbackPolicy",
                    "router": "draw2d.layout.connection.InteractiveManhattanConnectionRouter",
                    "source": {
                      "node": "3253ff2a-a920-09d5-f033-ca759a778e19",
                      "port": "output1"
                    },
                    "target": {
                      "node": "2810494b-931f-da59-fd9d-6deba4385fe0",
                      "port": "input0"
                    }
                  }
        elementUUID = 'f9735797cf1d8431d891c2d10f0a67be'
        addOrUpdateConnector(element, elementUUID, self.entity, self.entity)
        connector = Relationship.objects.get(smUUID=elementUUID)
        self.assertTrue(connector.code == connectorName)
