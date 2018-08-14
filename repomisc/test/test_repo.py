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
            "reponame": None
        }
        target.update(
            {key: value
             for key, value in data.items() if value is not None})
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
                "reponame": "mlmisc"
            })

        self.assertRepoUrl(
            "http://abc:bg@github.com/miacro/mlmisc", {
                "scheme": "http",
                "username": "abc",
                "password": "bg",
                "hostname": "github.com",
                "owner": "miacro",
                "reponame": "mlmisc",
            })
        self.assertRepoUrl(
            "git://ok:rf@github.com/miacro/mlmisc.git/", {
                "scheme": "git",
                "username": "ok",
                "password": "rf",
                "hostname": "github.com",
                "port": None,
                "owner": "miacro",
                "reponame": "mlmisc"
            })
        self.assertRepoUrl(
            "https://github.com/miacro/mlmisc/", {
                "scheme": "https",
                "hostname": "github.com",
                "owner": "miacro",
                "reponame": "mlmisc"
            })
        self.assertRepoUrl(
            "ftps://a:b@github.com:12345/miacro/mlmisc.git", {
                "scheme": "ftps",
                "username": "a",
                "password": "b",
                "hostname": "github.com",
                "port": "12345",
                "owner": "miacro",
                "reponame": "mlmisc"
            })
        self.assertRepoUrl("file:///abc/dfe", {
            "scheme": "file",
            "reponame": "dfe"
        })
        self.assertRepoUrl("file:///abc/def/hij/dddd.git", {
            "scheme": "file",
            "reponame": "dddd"
        })
        self.assertRepoUrl("/abc/def/hij/dddd", {
            "scheme": "file",
            "reponame": "dddd"
        })
        self.assertRepoUrl("/abc", {"reponame": "abc", "scheme": "file"})
        self.assertRepoUrl("/abc.git", {"reponame": "abc", "scheme": "file"})
        self.assertRepoUrl("/abc/def/../../dddd.git", {
            "reponame": "dddd",
            "scheme": "file"
        })
        self.assertRepoUrl("abc", {"reponame": "abc", "scheme": "file"})
        self.assertRepoUrl("./abc/../dfe/daff/dddd.git/", {
            "reponame": "dddd",
            "scheme": "file"
        })
        self.assertRepoUrl("../ddd/../dfidf/drt/gggagi.git", {
            "reponame": "gggagi",
            "scheme": "file"
        })
        self.assertRepoUrl(
            "git@github.com:~/miacro/mlmisc.git", {
                "reponame": "mlmisc",
                "username": "git",
                "hostname": "github.com",
                "owner": "miacro",
                "scheme": "ssh",
            })
        self.assertRepoUrl(
            "test@github.com:/abc/def/aaa.git", {
                "reponame": "aaa",
                "username": "test",
                "hostname": "github.com",
                "owner": "def",
                "scheme": "ssh",
            })
