import re


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


def urlparse(repourl):
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
        return ["(?P<{}>{})".format(name, patterns[name]) for name in names]

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
            for name in ["uri", "scp", "file", ""]:
                if name:
                    scheme_pattern = "^{}{}$".format(
                        name_patterns(name), postfix)
                else:
                    scheme_pattern = "^$".format(postfix)
                parseresult = re.fullmatch(scheme_pattern, repourl)
                if parseresult:
                    return parseresult

    matchresult = fullmatch()
    result = {
        name: None
        for name in ("scheme", "username", "password", "hostname", "port",
                     "owner", "reponame", "basicurl")
    }

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

    if not matchresult:
        return None
    if group_value("uri"):
        for name in [
                "scheme", "username", "password", "hostname", "port", "owner",
                "reponame"
        ]:
            result[name] = group_value(name)
        result["basicurl"] = group_value("uri")
    elif group_value("scp"):
        for name in ("username", "hostname", "owner", "reponame"):
            result[name] = group_value(name)
        result["scheme"] = "scp"
        result["basicurl"] = group_value("scp")
    elif group_value("file"):
        for name in ["reponame", "owner"]:
            result[name] = group_value(name)
        result["scheme"] = "file"
        result["basicurl"] = group_value("file")
    else:
        result["reponame"] = group_value("reponame")
        result["owner"] = group_value("owner")
    if result["reponame"] and result["reponame"][-4:] == ".git":
        result["reponame"] = result["reponame"][:-4]
    return result
