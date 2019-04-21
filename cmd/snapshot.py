import subprocess
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SnapshotData:
    window: str
    timestamp: float


class Snapshot:
    def get(self):
        # TODO: Add support for windows and mac as well
        return self.get_linux()

    def get_linux(self):
        bash_command = "xdotool getwindowfocus getwindowname".split(" ")
        result = subprocess.run(bash_command, capture_output=True)
        if result.returncode == 0 and not result.stderr:
            return SnapshotData(
                window=result.stdout.decode(),
                timestamp=datetime.now().timestamp()
            )
