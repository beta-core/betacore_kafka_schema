""" Unit test for avro class
"""
import unittest
from betacore.kafka.schema.avro import AvroSchema
import time
from .mock_server import make_server
class TestAvro(unittest.TestCase):
    """ Test Avro schema
    """

    @classmethod
    def setUpClass(cls):
        cls.serializer = AvroSchema()

        cls.proc = make_server('127.0.0.1', 5051, 'info')
        cls.proc.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()

    def test_encode_missing_schmea(self):
        """ Verify none is returned when passed in
        """
        self.assertRaises(AttributeError, self.serializer.encode, data={"test": "one"})

    def test_decode_missing_schmea(self):
        """ Verify none is returned when passed in
        """
        self.assertRaises(AttributeError, self.serializer.decode, data="hi")

    def test_encode_none(self):
        """ Verify none is returned when passed in
        """
        self.assertIsNone(self.serializer.encode(None))

    def test_decode_none(self):
        """ Verify none is returned when passed in
        """
        self.assertIsNone(self.serializer.decode(None))

    def test_encode_decode_with_schema(self):
        """ Test encode with schema
        """
        message = {
            "test": "body"
        }
        schmea = {
            "type": "record",
            "namespace": "betacore",
            "name": "Test entity",
            "fields": [
                {"name": "test", "type": "string"}
            ]
        }

        encode: bytes = self.serializer.encode(message, schema=schmea, schemaless=False)
        actual: dict =  self.serializer.decode(encode, schema=schmea, schemaless=False)
        self.assertDictEqual(message, actual)

    def test_encode_decode_with_out_schema(self):
        """ Test encode with schema
        """
        message = {
            "test": "body"
        }
        schmea = {
            "type": "record",
            "namespace": "betacore",
            "name": "Test entity",
            "fields": [
                {"name": "test", "type": "string"}
            ]
        }

        encode: bytes = self.serializer.encode(message, schema=schmea)
        actual: dict =  self.serializer.decode(encode, schema=schmea)
        self.assertDictEqual(message, actual)
