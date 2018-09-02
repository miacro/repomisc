from . import git
import logging
from . import repoutils
from . import errors
import subprocess


class Commands():
    def __init__(self, commands):
        if not commands:
            commands = {}
        for name, command in commands:
            setattr(self, name, command)
        for name in ("install", "reinstall", "uninstall"):
            if not hasattr(self, name):
                setattr(self, name, [])

    def __iter__(self):
        for name, value in vars(self).items():
            yield name, value

    def __setattr__(self, name, value):
        if isinstance(value, str):
            value = [value]
        elif isinstance(value, list) or isinstance(value, tuple):
            pass
        elif not value:
            value = []
        else:
            raise errors.CommandError("TypeError of command '{}'".format(name))
        return super().__setattr__(name, value)

    def run(self, name):
        if isinstance(name, str):
            names = [name]
        else:
            names = name
        for name in names:
            commands = getattr(self, name)
            for command in commands:
                result = subprocess.run(command, shell=True)
                if result.returncode != 0:
                    raise errors.CommandError(
                        "Execute '{}' command '{}' failed".format(
                            command, name))


class Repo():
    def __init__(self, **kwargs):
        attrnames = ("scheme", "username", "password", "hostname", "port",
                     "owner", "reponame", "basicurl", "repopath", "refspecs",
                     "commands")
        for name in attrnames:
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(self, name, None)
        for key in kwargs:
            assert key in attrnames, "Unrecognized attr '{}'".format(key)

        self.__repo = None

    def __repr__(self):
        return repr(vars(self))

    def __setattr__(self, name, value):
        if name == "reponame":
            if isinstance(value, str) and value[-4:] == ".git":
                value = value[:-4]
        elif name == "basicurl":
            if isinstance(value, str) and value[-1:] != "/":
                value = value + "/"
        elif name == "commands":
            value = Commands(value)
        return super().__setattr__(name, value)

    def url(self):
        for name in ("basicurl", "reponame"):
            assert getattr(
                self, name) is not None, "required attribute {}".format(name)
        if self.basicurl is None:
            basicurl = ""
        else:
            basicurl = self.basicurl
        if self.owner is None:
            return "{}{}.git".format(basicurl, self.reponame)
        return "{}{}/{}.git".format(basicurl, self.owner, self.reponame)

    def clone(self, verbosity=None):
        if verbosity:
            logging.log(
                repoutils.get_logging_level(verbosity),
                "Cloning {} into {}".format(self.url(), self.repopath))
        self.__repo = git.clone(self.url(), self.repopath)
        return self

    def init_repo(self, exists=True, empty=False, verbosity=None):
        repopath = git.discover(self.repopath)
        if repopath:
            if empty:
                raise errors.RepoError(
                    "already exists in {}".format(self.repopath),
                    reponame=self.reponame)
            else:
                if verbosity:
                    logging.log(
                        repoutils.get_logging_level(verbosity),
                        "Repo {} already exists in {}".format(
                            self.reponame, self.repopath))
                self.__repo = git.repo(repopath)
        else:
            if exists:
                raise errors.RepoError("not found", reponame=self.reponame)
            else:
                return self.clone(verbosity=verbosity)
        return self
