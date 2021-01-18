""" Avro Schema
"""
import io
from typing import Union, Optional

import fastavro
from .serializer import Serializer

class AvroSchema(Serializer):
    """ Serializer for Avro implementation
    """

    def encode(self, data: dict, **kwargs) -> Optional[bytes]:
        """ Encode the data into an avro byte stream
            
            :param data dict: information to be encoded into avro byte stream
   
            :param schema: schema to use in decode algorithm
            :type schema: Optional[dict]

            :param schemaless: encode without schmea defaults to true
            :type schemaless: Optional[dict]

            :return: bytes so long as data is not None
            :rtype: Optional[bytes]

            :raises AttributeError: schema must be provide with this implementation
            :rases fastavro.schema.SchemaParseException: incorrect schema provided, please verify the scheam is correct
        """
        if not data:
            return None
        _schema: dict = kwargs.get('schema', None)
        _schemaless: bool = kwargs.get('schemaless', True)
        if not _schema:
            raise AttributeError("Missing schema named argument")

        schema: fastavro = fastavro.parse_schema(_schema)
        stream: io.BytesIO = io.BytesIO()
        if _schemaless:
            fastavro.schemaless_writer(stream, schema, data)
            return stream.getvalue()
        fastavro.writer(stream, schema, [data])
        return stream.getvalue()

    def decode(self, data: Union[str, bytes], **kwargs) -> Optional[dict]:
        """ Decode the data into plane text
            
            :param data: data which needs to be decoded. both bytes and UTF-8 string allow
            :type data: Union[str, bytes]
            :param schema: schema to use in decode algorithm
            :type schema: Optional[dict]

            :raises AttributeError: schema must be provide with this implementation
        """
        if not data:
            return None
        _schema: dict = kwargs.get('schema', None)
        _schemaless: bool = kwargs.get('schemaless', True)
        if not _schema:
            raise AttributeError("Missing schema named argument")

        schema: fastavro = fastavro.parse_schema(_schema)
        stream: io.BytesIO = io.BytesIO(data)
        if _schemaless:
            return fastavro.schemaless_reader(stream, schema)
        return fastavro.reader(stream, schema).next()
