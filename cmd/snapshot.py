import subprocess
from datetime import datetime

from client.models.Snapshot import Snapshot


class TakeSnapshot:
    def get(self):
        # TODO: Add support for windows and mac as well
        return self.get_linux()

    def get_linux(self):
        # TODO: Handle errors gracefully and figure out a backup mechanism if the snapshot fails
        bash_command = "xprop -id $(xprop -root | grep \"_NET_ACTIVE_WINDOW(WINDOW)\" | " \
                       "awk 'NF>1{print $NF}') | grep \"WM_CLASS(STRING)\|WM_NAME(STRING)\""
        result = subprocess.run(bash_command, capture_output=True, check=True, text=True, shell=True)
        if result.returncode == 0 and not result.stderr:
            window_data = [el.split("=")[-1].strip().split(',')[-1]
                           for el in result.stdout.replace('"', '').strip().split("\n")]
            if len(window_data) == 1:
                window_data = [window_data[0], window_data[0]]
            return Snapshot(
                window_title=window_data[0],
                app_name=window_data[1],
                snap_time=datetime.now().timestamp()
            )
