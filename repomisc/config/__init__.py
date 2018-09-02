import pyconfigmanager as configmanager
import repomisc
import os
from repomisc import repoutils, errors
import logging
REPOSCHEMA = configmanager.getschema(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "reposchema.yaml"),
    pickname=None)


def getconfig(reposfile, repofile="repomisc.yaml"):
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
        repoabsfile = os.path.join(repo.repopath, repofile)
        if os.path.exists(repoabsfile) and os.path.isfile(repoabsfile):
            repoconfig = configmanager.getconfig(
                REPOSCHEMA, values=repoabsfile, pickname="repomisc")
        for name in ("reponame", "owner", "basicurl", "repopath"):
            assert (getattr(repo, name) is
                    not None), "{} of repo {} must not be None".format(
                        name, item["reponame"])
        repomiscconfig.repos[index] = repo
    repomiscconfig.repos = [
        item for item in repomiscconfig.repos if item is not None
    ]
    return repomiscconfig
