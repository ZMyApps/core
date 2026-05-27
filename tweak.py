import argparse
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import httpx

from shared import CydiaRepoInstance
from shared.config import CydiaRepoDebFile, GithubReleasesDebFile, get_tweak_config
from shared.repo import decrypted_latest_repo, decrypted_repo


def download_file(url: str, folder_path: Path, file_name: str | None = None):
    if not file_name:
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

    file_path = os.path.join(folder_path, file_name)
    with httpx.stream("GET", url) as r:
        with open(file_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return Path(file_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tweak_name")
    parser.add_argument("--app-version")
    parser.add_argument("--note")
    args = parser.parse_args()

    tweak_name = args.tweak_name
    app_version = args.app_version
    note = args.note

    app_config, tweak_config = get_tweak_config(tweak_name)

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        deb_paths: list[Path] = []
        ipa_path: Path | None = None
        tweak_version_label: str | None = None

        # Download tweaks
        if tweak_config and tweak_config.deb_files:
            for deb_info in tweak_config.deb_files:
                if isinstance(deb_info, CydiaRepoDebFile):
                    repo = CydiaRepoInstance(deb_info.repo)
                    if deb_info.version and deb_info.version != "latest":
                        # Specific deb version
                        package = repo.get_package(
                            bundle_identifier=deb_info.package, version=deb_info.version
                        )
                        deb_path = download_file(
                            url=package.download_url, folder_path=tmpdir
                        )
                        deb_paths.append(deb_path)
                    else:
                        # Latest deb version
                        package = repo.get_latest_package(
                            bundle_identifier=deb_info.package
                        )
                        deb_path = download_file(
                            url=package.download_url, folder_path=tmpdir
                        )
                        deb_paths.append(deb_path)
                        pass
                    if deb_info.use_version:
                        tweak_version_label = deb_info.version

                elif isinstance(deb_info, GithubReleasesDebFile):
                    repo = GithubRepo
                    pass

        # Download ipa
        pass

    # Download ipa
    ipa_asset_id: str | None = None
    if app_version and app_version != "latest":
        decrypted_repo.fetch()
        ipa_asset_id = decrypted_repo.get_app_specific(
            name=app_config.name, version=app_version
        ).asset_id
    else:
        decrypted_latest_repo.fetch()
        ipa_asset_id = decrypted_latest_repo.get_app_latest(
            name=app_config.name
        ).asset_id


if __name__ == "__main__":
    main()
