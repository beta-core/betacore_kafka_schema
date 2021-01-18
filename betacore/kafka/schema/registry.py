""" An implemention that works with the Schema Registry
    https://github.com/confluentinc/schema-registry
"""
import io
import json
import struct
from enum import Enum
from typing import Optional, Tuple, Union

import fastavro
import requests


from .serializer import Serializer
from .avro import AvroSchema

class SchemaRegistryMagicByteException(Exception):
    """ Magic Byte Exception
        The magic byte is incorrect
    """


class SchemaRegistryException(Exception):
    """  Schema Registry Exception
    """


class SchemaRegistryMode(str, Enum):
    """ Schema Mode used for deserializer
    """
    JSON: str = 'json'
    AVRO: str = 'avro'


class SchemaRegistry(Serializer):
    """  Schema Registry

        :param: Restrict the decode mode SchemaRegistryMode
    """

    MAGIC_BYTE: str = '>bI'
    MAGIC_BYTE_FRAME_SIZE: int = 5
    _cache: dict = {}

    url: str
    port: int
    ca_file: str
    avro: AvroSchema = AvroSchema()
    mode: SchemaRegistryMode

    def __init__(self, **kwargs):
        self.url = kwargs.pop('url', 'localhost')
        self.port = kwargs.pop('port', '5000')
        self.ca_file = kwargs.pop('ca_file', None)
        self.mode = kwargs.pop('mode', None)

    def decode_helper(self, data: Union[str, bytes]) -> Tuple[int, io.BytesIO]:
        """ Perimplemention we need to advance the byte stream per \
            :const:`SchemaRegistry.MAGIC_BYTE_FRAME_SIZE`

            :param Union[str, bytes] data: data to be decoded
        """
        encoded_data = io.BytesIO(data)

        zero_bit, schema_id = struct.unpack(
            self.MAGIC_BYTE,
            encoded_data.read(self.MAGIC_BYTE_FRAME_SIZE))
        if zero_bit != 0:
            raise SchemaRegistryMagicByteException(
                f"Magic Byte was {zero_bit} not 0."
                "Please verify that the information on the topic was encoded"
                "with the specification for kafka schmea registry")
        return schema_id, encoded_data

    def decode(self, data: Union[str, bytes], **kwargs) -> Optional[dict]:
        """ Decode the by getting the byte and schema id from the data stream and calling the scheam
            registry
        """
        if not data:
            return data
        _schema = kwargs.get('schema', None)
        schema_id, stream = self.decode_helper(data)
        schema: dict = _schema if _schema else self.get_from_registry(schema_id)
        if not self.mode or self.mode is SchemaRegistryMode.JSON:
            try:
                return json.load(stream)
            except json.JSONDecodeError as exception:
                if self.mode is SchemaRegistryMode.JSON:
                    raise exception

        try:
            return self.avro.decode(data=stream, scheam=schema)
        except fastavro.schema.SchemaParseException as exception:
            raise exception

    def get_from_registry(self, schema_id: int) -> dict:
        """
            Get from registry
            :param schema_id int: id index in schema
        """
        if schema_id in self._cache.keys():
            return self._cache[schema_id]

        url: str = f'{self.url}/schemas/ids/{schema_id}'
        result = requests.get(url, verify=self.ca_file)

        if result.status_code != 200:
            raise SchemaRegistryException("")

        _json: dict = result.json()
        _schema = json.loads(_json['scheam'])
        self._cache.update({schema_id: _schema})
        return _schema
