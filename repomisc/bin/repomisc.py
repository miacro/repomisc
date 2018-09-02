import pyconfigmanager as configmanager
import argparse
import os
import subprocess
import logging
from repomisc import errors
from repomisc.config import getconfig as getrepomiscconfig

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


def repos_update(repos):
    for name, repo in repos.items():
        olddir = os.getcwd()
        os.chdir(repo.repopath)
        subprocess.run(["git", "pull"])
        os.chdir(olddir)


def repos_push(repos):
    for name, repo in repos.items():
        olddir = os.getcwd()
        os.chdir(repo.repopath)
        subprocess.run(["git", "push", "origin"])
        os.chdir(olddir)


def repos_status(repos):
    for name, repo in repos.items():
        olddir = os.getcwd()
        os.chdir(repo.repopath)
        subprocess.run(["git", "status"])
        os.chdir(olddir)


def repos_init(config, exists=True, empty=True):
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
    repomiscconfig = getrepomiscconfig(config.repos)
    if config.command == "init":
        repos = repos_init(repomiscconfig, exists=False, empty=False)
        return
    repos = repos_init(repomiscconfig, exists=True, empty=False)
    if config.command == "update":
        repos_update(repos)
    elif config.command == "push":
        repos_push(repos)
    elif config.command == "status":
        repos_status(repos)


if __name__ == "__main__":
    main()
