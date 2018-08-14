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

    def __repr__(self):
        return repr(vars(self))

    def urlparse(self, repourl):

        attr_patterns = {
            "scheme": "(http[s]?)|(ssh)|(ftp)|(file)",
            "username": "[^/:@]+",
            "password": "[^/:@]+",
            "hostname": "[^/:@]+",
            "port": "[0-9]{1,6}",
            "owner": "[^/]+",
            "reponame": "[^/]+[^(.git)]",
        }
        patterns = {
            "basic":
            "^{}://({}(:{})?@)?{}(:{})?/{}/{}(.git)?$".format(
                *[
                    "(?P<{}>{})".format(attrname, attr_patterns[attrname])
                    for attrname in ("scheme", "username", "password",
                                     "hostname", "port", "owner", "reponame")
                ]),
            "file":
            "{}:///({}/)+{}(.git)?/?",
        }
        parseresult = re.fullmatch(patterns["basic"], repourl)

        for name in vars(self).keys():
            setattr(self, name, parseresult.group(name))


if __name__ == "__main__":
    repo = Repo()
    repo.urlparse("https://a:b@github.com/miacro/mlmisc")
    print(repo)
    repo.urlparse("http://a:b@github.com/miacro/mlmisc")
    print(repo)
    repo.urlparse("https://a:b@github.com/miacro/mlmisc.git")
    print(repo)
    repo.urlparse("https://github.com/miacro/mlmisc")
    print(repo)
    repo.urlparse("https://github.com:12345/miacro/mlmisc.git")
    print(repo)
