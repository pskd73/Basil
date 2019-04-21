from abc import abstractmethod, ABC

from cmd.snapshot import SnapshotData


class DataSource(ABC):

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, snapshot: SnapshotData):
        pass
