from cmd.data_sources.file_data_source import FileDataSource
from cmd.snapshot import Snapshot


class Basil:
    def run(self):
        # TODO: Get Data source type from config and pick the appropriate data source class
        data_source = FileDataSource()
        snapshot = Snapshot().get()
        data_source.write(snapshot)


if __name__ == "__main__":
    Basil().run()
