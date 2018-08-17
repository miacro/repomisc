import pyconfigmanager as configmanager
import argparse
import os
from repomisc import repoutils
import subprocess
import pygit2
import logging
import datetime

ARGSCHEMA = {
    "command": "",
    "repos": "",
    "run": {},
    "clone": {},
    "pull": {},
}

REPOSCHEMA = configmanager.getschema(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config",
        "reposchema.yaml"),
    pickname=None)


def init_repomisc_config(reposfile):
    repomiscconfig = configmanager.getconfig(
        REPOSCHEMA, values=reposfile, pickname="repomisc")
    for index, item in enumerate(repomiscconfig.repos):
        if isinstance(item, str):
            parseresult = repoutils.urlparse(item)
            if parseresult is None:
                logging.error("Invalid repo url: {}".format(item))
                repomiscconfig.repos[index] = None
                continue
            item = parseresult
        repo = repoutils.Repo(**item)
        for name in ("owner", "basicurl"):
            if getattr(repo, name) is None:
                setattr(repo, name, repomiscconfig.repo[name])
        if repo.repopath is None:
            repo.repopath = os.path.join(repomiscconfig.repo.repopath,
                                         repo.reponame)
        for name in ("reponame", "owner", "basicurl", "repopath"):
            assert (getattr(repo, name) is
                    not None), "{} of repo {} must not be None".format(
                        name, item["reponame"])
        repomiscconfig.repos[index] = repo
    repomiscconfig.repos = [
        item for item in repomiscconfig.repos if item is not None
    ]
    return repomiscconfig


def repo_clone(repos):
    for repo in repos:
        if not os.path.exists(repo.repopath):
            os.makedirs(repo.repopath)
        result = subprocess.run(["git", "clone", repo.url(), repo.repopath])


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
                print("\r{}\r".format(clear_message), end="")
                if stats.indexed_objects == stats.total_objects:
                    print(message, flush=True)
                else:
                    print(message, end="", flush=True)
                self.lasttime = currenttime
                self.lastreceived = stats.received_bytes
                self.lastlength = len(message)
        except Exception as e:
            logging.error(e)


def init_repos(config):
    repos = {}
    for repoconfig in config.repos:
        repopath = pygit2.discover_repository(repoconfig.repopath)
        if repopath:
            logging.info("Repo {} already exists in {}".format(
                repoconfig.reponame, repoconfig.repopath))
            repos[repoconfig.reponame] = pygit2.Repository(repopath)
        else:
            try:
                logging.info("Cloning {} into {}".format(
                    repoconfig.url(), repoconfig.repopath))
                repo = pygit2.clone_repository(
                    repoconfig.url(),
                    repoconfig.repopath,
                    callbacks=GitRemoteCallbacks())
                repos[repoconfig.reponame] = repo
            except pygit2.GitError as err:
                logging.error(err)
    return repos


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="repositories manager")
    config = configmanager.getconfig(schema=[
        ARGSCHEMA, {
            key: value
            for key, value in configmanager.getschema().items()
            if key in ("logging", "config")
        }
    ])
    config.update_values_by_argument_parser(
        parser=parser, subcommands=["run", "git"])
    if config.config.dump:
        config.dump_config(
            filename=config.config.dump, config_name="config.dump", exit=True)
    configmanager.logging.config(
        level=config.logging.verbosity, format="%(levelname)s: %(message)s")
    repomiscconfig = init_repomisc_config(config.repos)
    repos = init_repos(repomiscconfig)
    print(repos)


if __name__ == "__main__":
    main()
