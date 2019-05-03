import argparse
import time

from client.client import BasilClient
from snapshot import TakeSnapshot


class Basil:
    def run(self):
        client = BasilClient()
        snapshot = TakeSnapshot().get()
        client.send_snapshot(store='application_snapshots', snapshot_data=snapshot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A simple and modular time tracker')
    parser.add_argument('option', nargs='?', help='Options: get')
    parser.add_argument('--start', help='Input the start time if necessary')
    parser.add_argument('--end', help='Input the end time if necessary')
    args = parser.parse_args()
    if args and args.option == 'get':
        # TODO: Parse time and retrieve snapshots from db
        if args.start and args.end:
            pass
        elif args.start:
            pass
        else:
            print("Start time is needed, end time is optional")
    if args.option == 'add':
        # TODO: Add the ability to add projects
        pass
    if not args.option:
        while True:
            time.sleep(1 - time.monotonic() % 1)
            Basil().run()
