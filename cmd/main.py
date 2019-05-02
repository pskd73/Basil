import time

from client.client import BasilClient
from snapshot import TakeSnapshot


class Basil:
    def run(self):
        client = BasilClient()
        snapshot = TakeSnapshot().get()
        client.send_snapshot(store='application_snapshots', snapshot_data=snapshot)


if __name__ == "__main__":
    while True:
        time.sleep(1 - time.monotonic() % 1)
        Basil().run()
