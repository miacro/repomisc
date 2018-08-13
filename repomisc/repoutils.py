import re


def urlparse(repourl):
    patterns = []
    patterns.append("""^(?P<scheme>http[s]?)://\
(?P<username>[^/]+):(?P<password>[^/]+)@(?P<host>[^/]+)/(?P<owner>[^/]+)\
/(?P<repo>[^/]+[^(.git)])(.git)?$""")
    a = re.fullmatch(patterns[0], repourl)

    for name in ("scheme", "username", "password", "host", "owner", "repo"):
        print(a.group(name))


if __name__ == "__main__":
    urlparse("https://a:b@github.com/miacro/mlmisc")
    print("===")
    urlparse("http://a:b@github.com/miacro/mlmisc")
    print("===")
    urlparse("https://a:b@github.com/miacro/mlmisc.git")
