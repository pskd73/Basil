import subprocess
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SnapshotData:
    window_title: str
    program_name: str
    timestamp: float


class Snapshot:
    def get(self):
        # TODO: Add support for windows and mac as well
        return self.get_linux()

    def get_linux(self):
        bash_command = "xprop -id $(xprop -root | grep \"_NET_ACTIVE_WINDOW(WINDOW)\" | " \
                       "awk 'NF>1{print $NF}') | grep \"WM_CLASS(STRING)\|WM_NAME(STRING)\""
        result = subprocess.run(bash_command, capture_output=True, check=True, text=True, shell=True)
        if result.returncode == 0 and not result.stderr:
            window_data = [el.split("=")[-1].strip().split(',')[-1]
                           for el in result.stdout.replace('"', '').strip().split("\n")]
            return SnapshotData(
                window_title=window_data[0],
                program_name=window_data[1],
                timestamp=datetime.now().timestamp()
            )
