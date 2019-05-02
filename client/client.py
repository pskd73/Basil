import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from client.models.Snapshot import Snapshot


@dataclass
class BasilClient:
    # TODO: Read data from the config file first
    db_path: str = os.path.expanduser('~/basil.db')
    db_conn = sqlite3.connect(db_path)
    db_cur = db_conn.cursor()
    # Make this store independent
    db_cur.execute("""
        CREATE TABLE IF NOT EXISTS `application_snapshots` (
            `app_name`	TEXT NOT NULL,
            `window_title`	TEXT NOT NULL,
            `snap_time`	INTEGER NOT NULL,
            `duration`	INTEGER NOT NULL
        );""")
    db_conn.commit()

    def get_last_event_from_store(self, store: str) -> (Snapshot, int):
        last_record = self.db_cur.execute(f"select app_name, window_title, snap_time, duration from {store} "
                                          f"order by snap_time desc limit 1;").fetchone()
        if last_record is not None:
            return (
                Snapshot(app_name=last_record[0], window_title=last_record[1], snap_time=last_record[2]),
                last_record[3]
            )
        else:
            return None

    @staticmethod
    def _is_mergeable(old_snapshot: Snapshot, old_snap_duration: int, new_snapshot: Snapshot):
        snap_diff = int(new_snapshot.snap_time) - int(old_snapshot.snap_time)
        if (snap_diff == old_snap_duration) and (old_snapshot.window_title == new_snapshot.window_title):
            return True
        else:
            return False

    def get_snapshots(self, store: str, start_time: datetime, end_time: datetime):
        pass

    def send_snapshot(self, store: str, snapshot_data: Snapshot):
        last_event = self.get_last_event_from_store(store)
        if last_event is not None:
            last_snap, last_snap_duration = last_event[0], last_event[1]
            if self._is_mergeable(last_snap, last_snap_duration, snapshot_data):
                print("Merging with last snapshot")
                self.db_cur.execute(f"""
                                UPDATE {store}
                                SET duration=:new_duration
                                where snap_time=:snap_time
                                """, [last_snap_duration + 1, last_snap.snap_time])
                return
        print("Creating new snapshot")
        self.db_cur.execute(f"""
                INSERT INTO {store}
                (app_name, window_title, snap_time, duration)
                VALUES
                (:app_name,:window_title, :snap_time, 1);""", [
            snapshot_data.app_name,
            snapshot_data.window_title,
            snapshot_data.snap_time
        ])
        self.db_conn.commit()
