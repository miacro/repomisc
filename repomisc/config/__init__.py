import pyconfigmanager as configmanager
import repomisc
import os
from repomisc import repoutils
import logging
REPOSCHEMA = configmanager.getschema(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "reposchema.yaml"),
    pickname=None)


def getconfig(reposfile, repofile="repomisc.yaml"):
    def repomerge(repo, data):
        for name, value in data.items():
            origin_value = getattr(repo, name)
            if origin_value is None:
                setattr(repo, name, value)
            elif name == "commands":
                commands = origin_value
                for command_name in value:
                    if (not hasattr(commands, command_name)
                            or not getattr(commands, command_name)):
                        setattr(commands, command_name, value[command_name])

    repomiscconfig = configmanager.getconfig(
        REPOSCHEMA, values=reposfile)
    default_repoconfig = repomiscconfig.repo.values()
    for index, item in enumerate(repomiscconfig.repos):
        if isinstance(item, str):
            parseresult = repoutils.urlparse(item)
            if parseresult is None:
                logging.error("Invalid repo url: {}".format(item))
                repomiscconfig.repos[index] = None
                continue
            item = parseresult
        else:
            item = configmanager.getconfig(
                REPOSCHEMA["repo"], values=item).values()
        repo = repomisc.Repo(**item)
        if repo.repopath is None:
            repo.repopath = os.path.join(repomiscconfig.repo.repopath,
                                         repo.reponame)
        repoabsfile = os.path.join(repo.repopath, repofile)
        if os.path.exists(repoabsfile) and os.path.isfile(repoabsfile):
            repoconfig = configmanager.getconfig(
                REPOSCHEMA["repo"], values=repoabsfile)
            repomerge(
                repo, {
                    name: value
                    for name, value in repoconfig.values().items()
                    if name not in ("repopath", )
                })
        repomerge(
            repo, {
                name: value
                for name, value in default_repoconfig.items()
                if name not in ("repopath", "reponame")
            })
        for name in ("reponame", "owner", "basicurl", "repopath"):
            assert (getattr(repo, name) is
                    not None), "{} of repo {} must not be None".format(
                        name, item["reponame"])
        repomiscconfig.repos[index] = repo
    repomiscconfig.repos = [
        item for item in repomiscconfig.repos if item is not None
    ]
    return repomiscconfig
