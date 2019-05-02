# TODO: Only applies to window snapshots, need to make it more generic
class Snapshot:
    def __init__(self, window_title: str, app_name: str, snap_time: float):
        self.window_title = window_title
        self.app_name = app_name
        self.snap_time = snap_time
