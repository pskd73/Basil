import os
import sqlite3

from data_sources.data_source import DataSource
from snapshot import SnapshotData


class SqliteDataSource(DataSource):
    def read(self):
        pass

    def write(self, snapshot: SnapshotData):
        # TODO: Requires heavy refactoring, this is currently junk
        conn = sqlite3.connect(os.path.expanduser("~/basil.db"))
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `application_snapshots` (
            `program_name`	TEXT NOT NULL,
            `window_title`	TEXT NOT NULL,
            `event_timestamp`	INTEGER NOT NULL,
            `duration`	INTEGER NOT NULL
        );""")
        last_record = cursor.execute("select program_name, window_title, event_timestamp, duration from "
                                     "application_snapshots order by event_timestamp desc limit 1;")
        last_record = last_record.fetchall()
        if len(last_record) > 0:
            last_record = last_record[0]
            old_snapshot = SnapshotData(
                program_name=last_record[0],
                window_title=last_record[1],
                timestamp=last_record[2]
            )
            old_duration = last_record[3]
            timestamp_diff = int(snapshot.timestamp) - int(old_snapshot.timestamp)
            print(f"Old snapshot: {old_snapshot.__dict__}")
            print(f"New snapshot: {snapshot.__dict__}")
            if (timestamp_diff == old_duration) and (old_snapshot.window_title == snapshot.window_title):
                print("Merging with the previous record")
                # Merge with the old timestamp
                updated_duration = old_duration + 1
                cursor.execute("""
                UPDATE application_snapshots
                SET duration=:new_duration
                where event_timestamp=:event_timestamp
                """, [updated_duration, old_snapshot.timestamp])
                conn.commit()
            else:
                print("Creating new record")
                cursor.execute("""
                    INSERT INTO application_snapshots
                    (program_name, window_title, event_timestamp, duration)
                    VALUES
                    (:program_name,:window_title, :event_timestamp, 1);""",
                               [snapshot.program_name, snapshot.window_title, snapshot.timestamp])
                conn.commit()
        else:
            # DB does not have anything, Insert the first record
            print("Inserting first record")
            cursor.execute("""
                INSERT INTO application_snapshots
                (program_name, window_title, event_timestamp, duration)
                VALUES
                (:program_name,:window_title, :event_timestamp, 1);""",
                           [snapshot.program_name, snapshot.window_title, snapshot.timestamp])
            conn.commit()
