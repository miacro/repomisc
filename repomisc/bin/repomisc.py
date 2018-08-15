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


def urlparse(url):
    parseresult, validate = repoutils.urlparse(url)
    if validate:
        return {
            key: value
            for key, value in parseresult.items()
            if key in ("owner", "reponame", "basicurl")
        }
    else:
        return {"reponame": url, "owner": None, "basicurl": None}


def initrepos(reposfile):
    repomiscconfig = configmanager.getconfig(
        REPOSCHEMA, values=reposfile, pickname="repomisc")
    for index, item in enumerate(repomiscconfig.repos):
        if isinstance(item, str):
            item = urlparse(item)
        for name in ("owner", "basicurl"):
            if name not in item or item[name] is None:
                item[name] = repomiscconfig.repo[name]
        if "repopath" not in item or item["repopath"] is None:
            item["repopath"] = os.path.join(repomiscconfig.repo.repopath,
                                            item["reponame"])
        for name in ("reponame", "owner", "basicurl", "repopath"):
            assert (item[name] is
                    not None), "{} of repo {} should not be None".format(
                        name, item["reponame"])
        repomiscconfig.repos[index] = configmanager.getconfig(
            schema=REPOSCHEMA["repomisc"]["repo"], values=item)
    print(repomiscconfig)
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
