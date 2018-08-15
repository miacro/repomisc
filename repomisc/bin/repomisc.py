import pyconfigmanager as configmanager
import argparse
import os
import re
from repomisc import repoutils

ARGSCHEMA = {
    "command": "",
    "repos": "",
    "run": {},
    "git": {},
}

REPOSCHEMA = configmanager.getschema(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config",
        "reposchema.yaml"),
    pickname=None)


def initrepos(reposfile):
    repomiscconfig = configmanager.getconfig(
        REPOSCHEMA, values=reposfile, pickname="repomisc")
    for index, item in enumerate(repomiscconfig.repos):
        if isinstance(item, str):
            repo, validate = repoutils.urlparse(item)
            if not validate:
                repo.reponame = item
        else:
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
    for repo in repomiscconfig.repos:
        print(repo.url())
    return repomiscconfig


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
    configmanager.logging.config(level=config.logging.verbosity)
    initrepos(config.repos)


if __name__ == "__main__":
    main()
