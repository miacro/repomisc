import pyconfigmanager as configmanager
import argparse
import os

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
    print(repomiscconfig.repos)
    for item in repomiscconfig.repos:
        pass


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
