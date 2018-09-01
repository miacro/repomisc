import pyconfigmanager as configmanager
import argparse
import os
import repomisc
from repomisc import repoutils
import subprocess
import logging
from repomisc import errors

ARGSCHEMA = {
    "command": "",
    "repos": "",
    "run": {},
    "search": {
        "repodirs": [],
        "dumprepos": True,
    },
    "init": {},
    "update": {},
    "push": {},
    "status": {},
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
        repo = repomisc.Repo(**item)
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


def repo_update(repos):
    for name, repo in repos.items():
        olddir = os.getcwd()
        os.chdir(repo.repopath)
        result = subprocess.run(["git", "pull"])
        os.chdir(olddir)


def init_repos(config, exists=True, empty=True):
    repos = {}
    for repo in config.repos:
        try:
            repo.init_repo(exists=exists, empty=empty, verbosity="INFO")
            repos[repo.reponame] = repo
        except errors.GitError as e:
            logging.error(e)
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
        parser=parser,
        subcommands={
            "init": True,
            "status": True,
            "push": True,
            "search": True,
            "run": True,
            "update": True,
        })
    if config.config.dump:
        config.dump_config(filename=config.config.dump, exit=True)
    configmanager.logging.config(
        level=config.logging.verbosity, format="%(levelname)s: %(message)s")
    repomiscconfig = init_repomisc_config(config.repos)
    if config.command == "init":
        repos = init_repos(repomiscconfig, exists=False, empty=False)
        return
    repos = init_repos(repomiscconfig, exists=True, empty=False)
    if config.command == "update":
        repo_update(repos)
    elif config.command == "push":
        pass
    elif config.command == "status":
        pass
    else:
        print(repomiscconfig)


if __name__ == "__main__":
    main()
