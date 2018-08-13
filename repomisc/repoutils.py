import re


def urlparse(repourl):
    patterndict = {
        "scheme": "http[s]?",
        "username": "[^/]+",
        "password": "[^/]+",
        "host": "[^/]+",
        "owner": "[^/]+",
        "reponame": "[^/]+[^(.git)]",
    }
    patterns = []
    patterns.append(
        "^{}://{}:{}@{}/{}/{}(.git)?$".format(*[
            "(?P<{}>{})".format(item, patterndict[item])
            for item in ("scheme", "username", "password", "host", "owner",
                         "reponame")
        ]))
    a = re.fullmatch(patterns[0], repourl)

    for name in ("scheme", "username", "password", "host", "owner",
                 "reponame"):
        print(a.group(name))


if __name__ == "__main__":
    urlparse("https://a:b@github.com/miacro/mlmisc")
    print("===")
    urlparse("http://a:b@github.com/miacro/mlmisc")
    print("===")
    urlparse("https://a:b@github.com/miacro/mlmisc.git")
