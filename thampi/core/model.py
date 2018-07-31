import abc
from typing import Dict
from thampi.core.thampi_core import ThampiContext


class Model(object):
    __metaclass__ = abc.ABCMeta

    #
    # @abc.abstractmethod
    # def __init__(self,
    #              name: str,
    #              version: str,
    #              training_time_utc: datetime = None,
    #              instance_id: str = None,
    #              tags: Dict[str, str] = None) -> None:
    #     self._name = name
    #     self._version = version
    #     # TODO: Check training_time_utc is in UTC!
    #     self._training_time_utc = training_time_utc or util.utc_now()
    #     self._instance_id = instance_id or util.uuid()
    #     self._tags = tags

    @abc.abstractmethod
    def initialize(self, context: ThampiContext) -> None:
        pass

    @abc.abstractmethod
    def predict(self, args: Dict, context: ThampiContext) -> Dict:
        pass
