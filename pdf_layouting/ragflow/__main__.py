from ragflow import RagflowAPI
rapi = None
if __name__ == "__main_":
    rapi = RagflowAPI()
    rapi.deleteAssistantSessions("d1b1a76c0b0c11f08f5c0242ac120006",session_ids=["064458221f5711f0aaa10242ac120002"])