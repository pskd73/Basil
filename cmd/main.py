import time

from data_sources.sqlite_data_source import SqliteDataSource
from snapshot import Snapshot


class Basil:
    def run(self):
        # TODO: Get Data source type from config and pick the appropriate data source class
        data_source = SqliteDataSource()
        snapshot = Snapshot().get()
        data_source.write(snapshot)


if __name__ == "__main__":
    while True:
        time.sleep(1 - time.monotonic() % 1)
        Basil().run()
