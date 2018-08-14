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
        print(vars(repo))
        print(target)
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
            "https://ok:rf@github.com/miacro/mlmisc.git", {
                "scheme": "https",
                "username": "ok",
                "password": "rf",
                "hostname": "github.com",
                "port": None,
                "owner": "miacro",
                "reponame": "mlmisc"
            })
        self.assertRepoUrl(
            "https://github.com/miacro/mlmisc", {
                "scheme": "https",
                "hostname": "github.com",
                "owner": "miacro",
                "reponame": "mlmisc"
            })
        self.assertRepoUrl(
            "https://a:b@github.com:12345/miacro/mlmisc.git", {
                "scheme": "https",
                "username": "a",
                "password": "b",
                "hostname": "github.com",
                "port": "12345",
                "owner": "miacro",
                "reponame": "mlmisc"
            })
