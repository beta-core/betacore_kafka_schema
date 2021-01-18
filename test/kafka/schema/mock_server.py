""" Mock Server to be used in testing
"""
import json
from multiprocessing import Process
import uvicorn
from fastapi import FastAPI


class TestServer:
    """ Test Schmea Registry
    """
    schema = {
        "type": "record",
        "namespace": "betacore",
        "name": "Test entity",
        "fields": [
            {"name": "test", "type": "string"}
        ]
    }
    schemas = [schema]

    def __init__(self):
        self.app = FastAPI()
        self.app.get('/')(self.root)
        self.app.get('/schemas/ids/{schema_id}')(self.get_schema)

    async def root(self):
        """ root
        """
        return {"Hello": "World"}

    async def get_schema(self, schema_id: int):
        """ Simulate schmea endpoint
        """
        if not schema_id:
            raise Exception("")

        return {'scheam': json.dumps(self.schemas[schema_id])}


def make_server(host, port, log_level) -> Process:
    """ Get a process, each unit test file must run on diffrent port!
    """
    _api = TestServer()
    return Process(target=uvicorn.run, args=(_api.app,), kwargs={
        'host': host,
        'port':  port,
        'log_level': log_level
    })


def main():
    """ Run moc test server
    """
    server = TestServer()
    uvicorn.run(app=server.app, kwargs={
        'host': '127.0.0.1',
        'port':  5054,
        'log_level': 'info'
    })


if __name__ == '__main__':
    main()
