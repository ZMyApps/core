#!/usr/bin/env -S uv run

from shared import aNewerThanB, create_github_client
from shared.altsource import AltSourceApp, AltSourceRepo
from shared.config import GithubRepo, config, get_app_config

github_client = create_github_client()


def list_releases(github_repo: GithubRepo):
    return github_client.rest.paginate(
        github_client.rest.repos.list_releases,
        owner=github_repo.owner,
        repo=github_repo.repo,
        per_page=100,
    )


def upload_to_data(file_name: str, data: bytes):
    print(f"{file_name} - Uploading")
    # get release
    release = github_client.rest.repos.get_release_by_tag(
        owner=config.files_repo.owner,
        repo=config.files_repo.repo,
        tag=config.files_repo_json_tag,
    )
    # delete file if exists
    for asset in release.parsed_data.assets:
        if asset.name == file_name:
            github_client.rest.repos.delete_release_asset(
                owner=config.files_repo.owner,
                repo=config.files_repo.repo,
                asset_id=asset.id,
            )
            break
    # upload file
    github_client.request(
        "POST",
        release.parsed_data.upload_url.split("{?")[0],
        params={"name": file_name},
        content=data,
        headers={"Content-Type": "application/octet-stream"},
    )
    print(f"{file_name} - Uploaded")


def generate_decrypted():
    print("\ngenerate_decrypted()")
    all_apps: list[AltSourceApp] = []
    latest_apps: dict[str, AltSourceApp] = {}

    for release in list_releases(config.ipa_archive_repo):
        for asset in release.assets:
            splitted = asset.name.removesuffix(".ipa").split("_")
            if len(splitted) < 2 or len(splitted) > 3:
                print("Abnormal asset name length:", asset.name)
                continue
            app_name: str = splitted[0]
            app_version: str = splitted[1]
            app_config = get_app_config(name=app_name)
            if not app_config:
                print("App config not found:", app_name)
                continue
            current_app: AltSourceApp = AltSourceApp(
                name=app_name,
                bundleIdentifier=app_config.bundle_identifier,
                version=app_version,
                localizedDescription=asset.name,
                downloadURL=f"/download/{config.ipa_archive_repo.repo}/{asset.id}/{asset.name}",
                iconURL=f"/icon/{app_name}.jpg",
                versionDate=asset.created_at.isoformat(),
                size=asset.size,
            )
            all_apps.append(current_app)
            if app_name in latest_apps:
                version_in_latest = latest_apps[app_name].version
                if aNewerThanB(app_version, version_in_latest):
                    latest_apps[app_name] = current_app
            else:
                latest_apps[app_name] = current_app

    all_repo = AltSourceRepo(
        name="ZMyApps Decrypted",
        identifier="zmyapps.decrypted",
        iconURL="/icon.png",
        apps=sorted(all_apps, key=lambda x: x.versionDate, reverse=True),
    )

    upload_to_data(
        file_name="decrypted.json", data=all_repo.model_dump_json().encode("utf-8")
    )

    latest_repo = AltSourceRepo(
        name="ZMyApps Latest Decrypted",
        identifier="zmyapps.decrypted.latest",
        iconURL="/icon.png",
        apps=sorted(latest_apps.values(), key=lambda x: x.versionDate, reverse=True),
    )

    upload_to_data(
        file_name="decryptedlatest.json",
        data=latest_repo.model_dump_json().encode("utf-8"),
    )


def generate_tweaked():
    print("\ngenerate_tweaked()")
    all_apps: list[AltSourceApp] = []
    latest_apps: dict[str, AltSourceApp] = {}

    for release in list_releases(config.build_archive_repo):
        for asset in release.assets:
            splitted = asset.name.removesuffix(".ipa").split("_")
            if len(splitted) < 4 or len(splitted) > 5:
                print("Abnormal asset name length:", asset.name)
                continue
            app_name: str = splitted[0]
            app_version: str = splitted[1]
            tweak_name: str = splitted[2]
            tweak_version: str = splitted[3]
            app_config = get_app_config(name=app_name)
            if not app_config:
                print("App config not found:", app_name)
                continue
            current_app: AltSourceApp = AltSourceApp(
                name=tweak_name,
                bundleIdentifier=app_config.bundle_identifier,
                version=f"{app_version}_{tweak_version}",
                localizedDescription=asset.name,
                downloadURL=f"/download/{config.build_archive_repo.repo}/{asset.id}/{asset.name}",
                iconURL=f"/icon/{app_name}.jpg",
                versionDate=asset.created_at.isoformat(),
                size=asset.size,
            )
            all_apps.append(current_app)
            if app_name in latest_apps:
                version_in_latest = latest_apps[app_name].version
                if aNewerThanB(app_version, version_in_latest):
                    latest_apps[app_name] = current_app
            else:
                latest_apps[app_name] = current_app

    all_repo = AltSourceRepo(
        name="ZMyApps Tweaked",
        identifier="zmyapps.tweaked",
        iconURL="/icon.png",
        apps=sorted(all_apps, key=lambda x: x.versionDate, reverse=True),
    )

    upload_to_data(
        file_name="tweaked.json", data=all_repo.model_dump_json().encode("utf-8")
    )

    latest_repo = AltSourceRepo(
        name="ZMyApps Latest Tweaked",
        identifier="zmyapps.tweaked.latest",
        iconURL="/icon.png",
        apps=sorted(latest_apps.values(), key=lambda x: x.versionDate, reverse=True),
    )

    upload_to_data(
        file_name="tweakedlatest.json",
        data=latest_repo.model_dump_json().encode("utf-8"),
    )


def main():
    generate_decrypted()
    generate_tweaked()


if __name__ == "__main__":
    main()
