class GitError(Exception):
    pass


class RepoError(Exception):
    def __init__(self, message, reponame=None):
        if reponame:
            if isinstance(message, dict):
                message.update({"reponame": reponame})
            else:
                message = "Repo {} {}".format(reponame, message)
        self.reponame = reponame
        super(RepoError, self).__init__(message)
