import pyconfigmanager as configmanager
import argparse
SCHEMA = {
    "command": "",
    "run": {},
    "git": {},
}


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="repositories manager")
    config = configmanager.getconfig(schema=[
        SCHEMA, {
            key: value
            for key, value in configmanager.getschemas().items()
            if key in ("logging", "config")
        }
    ])
    config.update_values_by_argument_parser(
        parser=parser, subcommands=["run", "git"])
    if config.config.dump:
        config.dump_config(
            filename=config.config.dump, config_name="config.dump", exit=True)
    configmanager.logging.config(level=config.logging.verbosity)
    print(config)


if __name__ == "__main__":
    main()
