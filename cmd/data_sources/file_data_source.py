import json
import os
from datetime import datetime

from data_sources.data_source import DataSource


class FileDataSource(DataSource):
    # TODO: Rewrite this to use CSV maybe?
    def read(self):
        pass

    def write(self, snapshot):
        capture_datetime = datetime.fromtimestamp(snapshot.timestamp)
        dir_path = os.path.expanduser(
            f"~/.basil/{capture_datetime.year}/{capture_datetime.month}/{capture_datetime.day}")
        file_path = os.path.join(dir_path, "snapshots.json")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        try:
            file = open(file_path, 'r+')
        except IOError:
            file = open(file_path, 'w+')
        contents = file.read()
        file.seek(0)
        if not contents:
            file.write(json.dumps([snapshot.__dict__]))
        else:
            existing_data: list = json.loads(contents)
            existing_data.append(snapshot.__dict__)
            file.write(json.dumps(existing_data), )
