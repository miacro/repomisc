import pygit2
import logging
import datetime
import sys
from . import errors


class GitRemoteCallbacks(pygit2.remote.RemoteCallbacks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lasttime = None
        self.lastreceived = 0
        self.lastspeed = 0
        self.lastlength = 0

    def readableunits(self, value):
        power = 1024
        for unit in ("Bytes", "KiB", "MiB", "GiB", "TiB"):
            if value >= power:
                value = value / power
            else:
                break
        return value, unit

    def transfer_progress(self, stats):
        """
        Args:
          stats.indexed_deltas,   stats.indexed_objects
          stats.local_objects,    stats.received_bytes
          stats.received_objects, stats.total_deltas
          stats.total_objects
        """
        try:
            currenttime = datetime.datetime.now()
            if self.lasttime is not None:
                interval = currenttime - self.lasttime
                interval = interval.total_seconds()
            else:
                interval = 0
                self.lasttime = currenttime
            if interval > 1 or (stats.indexed_objects == stats.total_objects):
                if interval > 1:
                    self.lastspeed = (
                        stats.received_bytes - self.lastreceived) / interval
                speed, speed_unit = self.readableunits(self.lastspeed)
                received_bytes, received_bytes_unit = self.readableunits(
                    stats.received_bytes)
                clear_message = "".join([" " for _ in range(self.lastlength)])
                message = (
                    "Receiving objects:" +
                    " {:>2.2%} ({}/{}), {:.2f} {} | {:.2f} {}/s").format(
                        stats.received_objects / stats.total_objects,
                        stats.received_objects, stats.total_objects,
                        received_bytes, received_bytes_unit, speed, speed_unit)
                print("\r{}\r".format(clear_message), end="", file=sys.stderr)
                if stats.indexed_objects == stats.total_objects:
                    print(message, flush=True, file=sys.stderr)
                else:
                    print(message, end="", flush=True, file=sys.stderr)
                self.lasttime = currenttime
                self.lastreceived = stats.received_bytes
                self.lastlength = len(message)
        except Exception as e:
            logging.error(e)


def clone(repourl, repopath):
    try:
        return pygit2.clone_repository(
            repourl, repopath, callbacks=GitRemoteCallbacks())
    except pygit2.GitError as e:
        raise errors.GitError(e)


def discover(repopath):
    return pygit2.discover_repository(repopath)


def repo(repopath):
    return pygit2.Repository(repopath)
