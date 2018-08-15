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
        self.basicurl = None

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

        def name_patterns(names):
            if isinstance(names, str):
                return "(?P<{}>{})".format(names, patterns[names])
            return [
                "(?P<{}>{})".format(name, patterns[name]) for name in names
            ]

        patterns["uri"] = "{}://({}(:{})?@)?{}(:{})?(/{})*/".format(
            name_patterns("scheme"), name_patterns("username"),
            name_patterns("password"), name_patterns("hostname"),
            name_patterns("port"), patterns["dirname"])
        patterns["scp"] = "{}@{}:/?({}/)*".format(
            name_patterns("username"), name_patterns("hostname"),
            patterns["dirname"])
        patterns["file"] = "((file://)?/)?({}/)*".format(patterns["dirname"])

        def fullmatch():
            for postfix in [
                    "{}/{}/?".format(*name_patterns(["owner", "reponame"])),
                    "{}/?".format(name_patterns("reponame"))
            ]:
                for name in ["uri", "scp", "file"]:
                    scheme_pattern = "^{}{}$".format(
                        name_patterns(name), postfix)
                    parseresult = re.fullmatch(scheme_pattern, repourl)
                    if parseresult:
                        return parseresult

        matchresult = fullmatch()

        def group_value(name):
            try:
                if not name:
                    if not matchresult:
                        return None
                    else:
                        return matchresult.string
                return matchresult.group(name)
            except IndexError:
                return None

        def setattrs(names):
            for name in vars(self).keys():
                if name in names:
                    setattr(self, name, group_value(name))
                else:
                    setattr(self, name, None)
            self.url = group_value(None)

        if not matchresult:
            setattrs([])
            return
        if group_value("uri"):
            setattrs([
                "scheme", "username", "password", "hostname", "port", "owner",
                "reponame"
            ])
            self.basicurl = group_value("uri")
        elif group_value("scp"):
            setattrs(("username", "hostname", "owner", "reponame"))
            self.scheme = "scp"
            self.basicurl = group_value("scp")
        elif group_value("file"):
            setattrs(["reponame", "owner"])
            self.scheme = "file"
            self.basicurl = group_value("file")


def urlparse(url):
    repo = Repo()
    repo.urlparse(url)
    return vars(repo), repo.url
