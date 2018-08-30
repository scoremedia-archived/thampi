import abc
from typing import Dict
from thampi.core.thampi_core import ThampiContext


class Model(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, context: ThampiContext) -> None:
        pass

    @abc.abstractmethod
    def predict(self, args: Dict, context: ThampiContext) -> Dict:
        pass
