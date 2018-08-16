import pyconfigmanager as configmanager
import argparse
import os
from repomisc import repoutils
import subprocess
import pygit2
import logging

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
                item = {"reponame": item}
            else:
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
    return repomiscconfig


def repo_clone(repos):
    for repo in repos:
        if not os.path.exists(repo.repopath):
            os.makedirs(repo.repopath)
        result = subprocess.run(["git", "clone", repo.url(), repo.repopath])


class GitRemoteCallbacks(pygit2.remote.RemoteCallbacks):
    def transfer_progress(self, stats):
        print("\r", end="")
        print(
            "{} {} {} {} {} {} {}".format(
                stats.indexed_deltas, stats.indexed_objects,
                stats.local_objects, stats.received_bytes,
                stats.received_objects, stats.total_deltas,
                stats.total_objects),
            end="",
            flush=True)


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
