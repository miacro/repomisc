import unittest
from repomisc.repoutils import Repo


class RepoTest(unittest.TestCase):
    def assertRepoUrl(self, url, data):
        target = {
            "scheme": None,
            "username": None,
            "password": None,
            "hostname": None,
            "port": None,
            "owner": None,
            "reponame": None,
            "url": None,
            "basicurl": None,
        }
        if data:
            target["url"] = url
            target.update({
                key: value
                for key, value in data.items() if value is not None
            })
        repo = Repo()
        repo.urlparse(url)
        self.assertDictEqual(vars(repo), target)

    def test_urlparse(self):
        self.assertRepoUrl(
            "https://aaa:bbb@github.com/miacro/mlmisc", {
                "scheme": "https",
                "username": "aaa",
                "password": "bbb",
                "hostname": "github.com",
                "owner": "miacro",
                "reponame": "mlmisc",
                "basicurl": "https://aaa:bbb@github.com/",
            })

        self.assertRepoUrl(
            "http://abc:bg@github.com/miacro/mlmisc", {
                "scheme": "http",
                "username": "abc",
                "password": "bg",
                "hostname": "github.com",
                "owner": "miacro",
                "reponame": "mlmisc",
                "basicurl": "http://abc:bg@github.com/",
            })
        self.assertRepoUrl(
            "git://ok:rf@github.com/miacro/mlmisc.git/", {
                "scheme": "git",
                "username": "ok",
                "password": "rf",
                "hostname": "github.com",
                "port": None,
                "owner": "miacro",
                "reponame": "mlmisc",
                "basicurl": "git://ok:rf@github.com/",
            })
        self.assertRepoUrl(
            "https://github.com/miacro/mlmisc/", {
                "scheme": "https",
                "hostname": "github.com",
                "owner": "miacro",
                "reponame": "mlmisc",
                "basicurl": "https://github.com/",
            })
        self.assertRepoUrl("https://github.com", {})
        self.assertRepoUrl(
            "ftps://a:b@github.com:12345/miacro/mlmisc.git", {
                "scheme": "ftps",
                "username": "a",
                "password": "b",
                "hostname": "github.com",
                "port": "12345",
                "owner": "miacro",
                "reponame": "mlmisc",
                "basicurl": "ftps://a:b@github.com:12345/",
            })
        self.assertRepoUrl(
            "file:///abc/dfe", {
                "scheme": "file",
                "owner": "abc",
                "reponame": "dfe",
                "basicurl": "file:///",
            })
        self.assertRepoUrl(
            "file:///abc/def/hij/dddd.git", {
                "scheme": "file",
                "owner": "hij",
                "reponame": "dddd",
                "basicurl": "file:///abc/def/",
            })
        self.assertRepoUrl(
            "/abc/def/hij/dddd", {
                "scheme": "file",
                "owner": "hij",
                "reponame": "dddd",
                "basicurl": "/abc/def/",
            })
        self.assertRepoUrl("/abc", {
            "scheme": "file",
            "basicurl": "/",
            "reponame": "abc",
        })
        self.assertRepoUrl("/abc.git", {
            "scheme": "file",
            "reponame": "abc",
            "basicurl": "/",
        })
        self.assertRepoUrl(
            "/abc/def/../../dddd.git", {
                "reponame": "dddd",
                "owner": "..",
                "scheme": "file",
                "basicurl": "/abc/def/../",
            })
        self.assertRepoUrl("abc", {})
        self.assertRepoUrl(
            "./abc/../dfe/daff/dddd.git/", {
                "reponame": "dddd",
                "owner": "daff",
                "scheme": "file",
                "basicurl": "./abc/../dfe/",
            })
        self.assertRepoUrl(
            "../ddd/../dfidf/drt/gggagi.git", {
                "reponame": "gggagi",
                "owner": "drt",
                "scheme": "file",
                "basicurl": "../ddd/../dfidf/",
            })
        self.assertRepoUrl(
            "git@github.com:~/miacro/mlmisc.git", {
                "reponame": "mlmisc",
                "username": "git",
                "hostname": "github.com",
                "owner": "miacro",
                "scheme": "scp",
                "basicurl": "git@github.com:~/",
            })
        self.assertRepoUrl(
            "test@github.com:/abc/def/aaa.git", {
                "reponame": "aaa",
                "username": "test",
                "hostname": "github.com",
                "owner": "def",
                "scheme": "scp",
                "basicurl": "test@github.com:/abc/",
            })
