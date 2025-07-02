import os
from dotenv import load_dotenv
import requests
from datetime import datetime

env = load_dotenv()

class RagflowAPI:
    def __init__(self):
        self.host = os.getenv("RAGFLOW_HOST")
        self.port = os.getenv("RAGFLOW_PORT")
        self.api_key = os.getenv("RAGFLOW_API_KEY")
        self.protocol = "http"
        self.url_prefix = f"{self.protocol}://{self.host}:{self.port}"

    def createDataset(self,name):
        url = f"{self.url_prefix}/api/v1/datasets"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            'name':name
        }

        r = requests.post(url ,headers = headers, json=payload)
        return r.json()

    def addDocument(self,document_path,dataset_id):
        url = f"{self.url_prefix}/api/v1/datasets/{dataset_id}/documents"
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        with open(document_path, 'rb') as file:
            files = {'file': open(document_path, 'rb')}

        r = requests.post(url ,headers = headers, files=files)
        return r.json()

    def createChunk(self,chunk,document_id,dataset_id):
        url = f"{self.url_prefix}/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            'content':chunk
        }

        r = requests.post(url ,headers = headers, json=payload)
        return r.json()
    
    def getSessionsByAssistantId(self,assistant_id,filter=None):
        url = f"{self.url_prefix}/api/v1/chats/{assistant_id}/sessions?page_size=99999"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        r = requests.get(url ,headers = headers)
        sessions = r.json()["data"]
        return sessions
    
    def getDatasets(self, filter=None):
        url = f"{self.url_prefix}/api/v1/datasets?page_size=99999"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        r = requests.get(url ,headers = headers)
        datasets = r.json()["data"]
        if filter != None:
            return [dataset for dataset in datasets if filter(dataset)]
        else:
            return datasets
        
    def deleteAssistantSessions(self,assistant_id,session_ids=None,filter=None):
        if(session_ids==None and filter==None):
            raise Exception("specify either 'session_ids' or 'filter' when calling deleteAssistantSessions")
        
        sessions = self.getSessionsByAssistantId(assistant_id,filter)
        ids = [session["id"] for session in sessions]
        if session_ids != None:
            ids = [id for id in ids if id in session_ids]
        print(f"deleting sessions with ids: {ids}")
        url = f"{self.url_prefix}/api/v1/chats/{assistant_id}/sessions"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            'ids':ids
        }

        r = requests.delete(url ,headers = headers, json=payload)
        return r.json()
    
    
    def deleteDatasets(self,dataset_ids=None,filter=None):
        if(dataset_ids==None and filter==None):
            raise Exception("specify either 'dataset_ids' or 'filter' when calling deleteAssistantSessions")
        
        datasets = self.getDatasets(filter)
        ids = [session["id"] for session in datasets]
        if dataset_ids != None:
            ids = [id for id in ids if id in dataset_ids]
        
        print(f"deleting datasets with ids: {ids}")
        url = f"{self.url_prefix}/api/v1/datasets"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            'ids':ids
        }

        r = requests.delete(url ,headers=headers, json=payload)
        return r.json()
    
    def deleteDataset(self,dataset_id):
        url = f"{self.url_prefix}/api/v1/datasets"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            'ids':[dataset_id]
        }

        r = requests.delete(url ,headers = headers, json=payload)
        return r.json()
    
    def deleteAssistantSession(self,assistant_id,session_id):
        url = f"{self.url_prefix}/api/v1/chats/{assistant_id}/sessions"
        headers = {
            'Content-Type':'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            'ids':[session_id]
        }

        r = requests.delete(url ,headers = headers, json=payload)
        return r.json()

if __name__ == "__main__":
    rapi = RagflowAPI()