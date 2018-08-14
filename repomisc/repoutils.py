import re


class Repo():
    def __init__(self):
        self.scheme = None
        self.username = None
        self.password = None
        self.hostname = None
        self.port = None
        self.owner = None
        self.reponame = None
        self.url = None

    def __repr__(self):
        return repr(vars(self))

    def __setattr__(self, name, value):
        if name == "reponame" and value and value[-4:] == ".git":
            value = value[:-4]
        return super().__setattr__(name, value)

    def urlparse(self, repourl):
        patterns = {
            "scheme": "(http[s]?)|(ssh)|(ftp[s]?)|(git)",
            "username": "[^/:@]+",
            "password": "[^/:@]+",
            "hostname": "[^/:@]+",
            "port": "[0-9]{1,6}",
            "owner": "[^/]+",
            "reponame": "[^/]+",
            "dirname": "([^/]+)",
        }

        def pattern_groups(names):
            if isinstance(names, str):
                return "(?P<{}>{})".format(names, patterns[names])
            return [
                "(?P<{}>{})".format(name, patterns[name]) for name in names
            ]

        patterns["uri"] = "^{}://({}(:{})?@)?{}(:{})?(/{})*/{}/{}/?$".format(
            pattern_groups("scheme"), pattern_groups("username"),
            pattern_groups("password"), pattern_groups("hostname"),
            pattern_groups("port"), patterns["dirname"],
            pattern_groups("owner"), pattern_groups("reponame"))
        patterns["scp"] = "^({}@)?{}:/?({}/)*{}/{}/?$".format(
            pattern_groups("username"), pattern_groups("hostname"),
            patterns["dirname"], pattern_groups("owner"),
            pattern_groups("reponame"))
        patterns["file"] = "^((file://)?/)?({}/)*{}/?$".format(
            patterns["dirname"], pattern_groups("reponame"))

        parseresult = re.fullmatch(patterns["uri"], repourl)

        def setattrs(names):
            for name in vars(self).keys():
                if name in names:
                    setattr(self, name, parseresult.group(name))
                else:
                    setattr(self, name, None)
            self.url = parseresult.string

        if parseresult:
            setattrs([
                "scheme", "username", "password", "hostname", "port", "owner",
                "reponame"
            ])
            return
        parseresult = re.fullmatch(patterns["scp"], repourl)
        if parseresult:
            setattrs(("username", "hostname", "owner", "reponame"))
            self.scheme = "ssh"
            return
        parseresult = re.fullmatch(patterns["file"], repourl)
        if parseresult:
            setattrs(["reponame"])
            self.scheme = "file"
