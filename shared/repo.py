from shared import parse_version
from shared.altsource import AltSourceRepo

from .config import config
from .github import create_github_client

github_client = create_github_client()


def get_repo(file_name: str):
    release = github_client.rest.repos.get_release_by_tag(
        owner=config.files_repo.owner,
        repo=config.files_repo.repo,
        tag=config.files_repo_json_tag,
    )
    for asset in release.parsed_data.assets:
        if asset.name == file_name:
            file = github_client.rest.repos.get_release_asset(
                owner=config.files_repo.owner,
                repo=config.files_repo.repo,
                asset_id=asset.id,
                headers={"Accept": "application/octet-stream"},
            )
            return AltSourceRepo.model_validate_json(file.content)


class RepoJson:
    def __init__(self, file_name: str):
        self.file_name: str = file_name

    def fetch(self):
        repo = get_repo(file_name=self.file_name)
        if repo:
            self.repo: AltSourceRepo = repo

    def filter_apps(
        self, name: str | None = None, bundle_identifier: str | None = None
    ):
        if name:
            return [app for app in self.repo.apps if app.name == name]
        elif bundle_identifier:
            return [
                app
                for app in self.repo.apps
                if app.bundleIdentifier == bundle_identifier
            ]

    def get_app_latest(
        self, name: str | None = None, bundle_identifier: str | None = None
    ):
        filtered = self.filter_apps(name=name, bundle_identifier=bundle_identifier)
        if filtered:
            sorted_filtered = sorted(filtered, key=lambda x: parse_version(x.version))
            return sorted_filtered[-1]

    def get_app_specific(
        self,
        version: str,
        name: str | None = None,
        bundle_identifier: str | None = None,
    ):
        filtered = self.filter_apps(name=name, bundle_identifier=bundle_identifier)
        if filtered:
            for app in filtered:
                if app.version == version:
                    return app


decrypted_repo = RepoJson(file_name="decrypted.json")
decrypted_latest_repo = RepoJson(file_name="decryptedlatest.json")
tweaked_repo = RepoJson(file_name="tweaked.json")
tweaked_latest_repo = RepoJson(file_name="tweakedlatest.json")
