""" Serialization
"""
from typing import Any
from abc import abstractmethod, ABC


class Serializer(ABC):
    """ Abstract  interface which defines Serializer operations.
    """
    @abstractmethod
    def encode(self, data, **kwargs)-> Any:
        """ Encode the data into implementation classes format
        """

    @abstractmethod
    def decode(self,data, **kwargs)-> Any:
        """ Decode the data into plane text
        """
