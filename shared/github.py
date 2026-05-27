import os
import subprocess
from functools import cache

from githubkit import GitHub
from githubkit.auth import ActionAuthStrategy, TokenAuthStrategy

from shared.config import GithubRepo, config


@cache
def create_github_client() -> GitHub:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return GitHub(ActionAuthStrategy())

    token = _get_local_github_token()
    return GitHub(TokenAuthStrategy(token))


def _get_local_github_token() -> str:
    result = subprocess.run(
        ["gh", "auth", "token", "--user", config.local_username],
        check=True,
        capture_output=True,
        text=True,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError(
            f"gh auth token returned an empty token for {config.local_username!r}"
        )
    return token


class GithubRepoInstance:
    def __init__(self, repo: GithubRepo):
        self.repo = repo

    def get_release_asset(
        self,
        latest: bool = False,
        tag: str | None = None,
        endswith: str | None = None,
    ):
        release = None
        if latest:
            release = create_github_client().rest.repos.get_latest_release(
                owner=self.repo.owner, repo=self.repo.repo
            )
        elif tag:
            release = create_github_client().rest.repos.get_release_by_tag(
                owner=self.repo.owner, repo=self.repo.repo, tag=tag
            )
        pass

        return
