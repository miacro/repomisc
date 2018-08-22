from . import git
import logging
from . import repoutils


class Repo():
    def __init__(self, **kwargs):
        attrnames = ("scheme", "username", "password", "hostname", "port",
                     "owner", "reponame", "basicurl", "repopath", "refspecs")
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
        if isinstance(value, str) and value:
            if name == "reponame" and value[-4:] == ".git":
                value = value[:-4]
            if name == "basicurl" and value[-1:] != "/":
                value = value + "/"
        return super().__setattr__(name, value)

    def url(self):
        for name in ("basicurl", "reponame"):
            assert getattr(
                self, name) is not None, "required attribute {}".format(name)
        if self.owner is None:
            return "{}{}.git".format(self.basicurl, self.reponame)
        return "{}{}/{}.git".format(self.basicurl, self.owner, self.reponame)

    def clone(self, verbosity=None):
        if verbosity:
            logging.log(
                repoutils.get_logging_level(verbosity),
                "Cloning {} into {}".format(self.url(), self.repopath))
        self.__repo = git.clone(self.url(), self.repopath)
        return self

    def init_repo(self, clone=True, exists=True, verbosity=None):
        repopath = git.discover(self.repopath)
        if repopath:
            if exists:
                if verbosity:
                    logging.log(
                        repoutils.get_logging_level(verbosity),
                        "Repo {} already exists in {}".format(
                            self.reponame, self.repopath))
                self.__repo = git.repo(repopath)
            else:
                raise Exception("Repo {} already exists in {}".format(
                    self.reponame, self.repopath))
        else:
            if clone:
                return self.clone(verbosity=verbosity)
            else:
                raise Exception("Repo {} not foune".format(self.reponame))
        return self
