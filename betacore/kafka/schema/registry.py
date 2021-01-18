""" An implemention that works with the Schema Registry
    https://github.com/confluentinc/schema-registry

    .. warning ::
        This functionality is still in beta and may be removed at future date
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
    """  Schema Registry Client 

        :param Optional[SchemaRegistryMode] mode: Restrict the decode mode SchemaRegistryMode
        :param Optional[str] url: url address of schmea repository, you can also use ip address default localhost
        :param Optional[str] ca_file: certificate file path, usefull if behind a proxy default None
        :param Optional[int] port: port of schema repository default 5000

    """
    #: schema registry magic byte
    MAGIC_BYTE: str = '>bI'
    #: the size of the magic byte frame which needs to be adjusted for
    MAGIC_BYTE_FRAME_SIZE: int = 5
    #: cache, will save schmeas to a local memory cache to save of rest calls
    _cache: dict = {}
    #: url address of schmea repository, you can also use ip address
    url: str
    #: port of schema repository
    port: int
    #: certificate file path, usefull if behind a proxy 
    ca_file: str
    #: avro decoder instance
    avro: AvroSchema = AvroSchema()
    mode: SchemaRegistryMode

    def __init__(self, **kwargs):
        self.url = kwargs.pop('url', 'localhost')
        self.port = kwargs.pop('port', '5000')
        self.ca_file = kwargs.pop('ca_file', None)
        self.mode = kwargs.pop('mode', None)

    def decode_helper(self, data: Union[str, bytes]) -> Tuple[int, io.BytesIO]:
        """
            Preforms check on the  :const:`SchemaRegistry.MAGIC_BYTE` if present \
            perimplemention advance the byte stream per \
            :const:`SchemaRegistry.MAGIC_BYTE_FRAME_SIZE`
            
            :param data: data to be decoded
            :type data: Union[str, bytes]

            :return: tuple with the schema id number and the encoded datasteam. 
            :rtype: Tuple[int, io.BytesIO]

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

            :param data: data which needs to be decoded. both bytes and UTF-8 string allow
            :type data: Union[str, bytes]
            :param schema: schema to use in decode algorithm
            :type schema: Optional[dict]

            :return: value of decoded message if data is is present
            :rtype: Optional[dict]
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
            Get from schema registry restful api

            :param int schema_id: id index in schema
            :return: schmea payload from registry api
            :rtype: dict
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
