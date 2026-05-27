import gzip
from urllib.parse import urljoin

import httpx
from debian import deb822, debian_support


class CydiaPackage(deb822.Packages):
    def __init__(self, repo: CydiaRepoInstance, package: deb822.Packages):
        super().__init__(package)
        self.repo = repo

    @property
    def download_url(self):
        return self.repo.join_package_full_url(self["Filename"])


class CydiaRepoInstance:
    def __init__(self, url: str):
        self.url = url
        packages_gz_url = f"{self.url}/Packages.gz"
        response = httpx.get(packages_gz_url)
        content = gzip.decompress(response.content).decode("utf-8")
        self.packages = list(deb822.Packages.iter_paragraphs(content))

    def filter_packages(self, bundle_identifier: str):
        return [pkg for pkg in self.packages if pkg["Package"] == bundle_identifier]

    def get_latest_package(self, bundle_identifier: str):
        filtered_list = self.filter_packages(bundle_identifier)
        sorted_list = sorted(
            filtered_list,
            key=lambda p: debian_support.Version(p["Version"]),
        )
        return CydiaPackage(repo=self, package=sorted_list[-1])

    def get_package(self, bundle_identifier: str, version: str):
        filtered_list = self.filter_packages(bundle_identifier)
        for item in filtered_list:
            if item["Version"] == version:
                return CydiaPackage(repo=self, package=item)

    def join_package_full_url(self, relative_url: str):
        return urljoin(f"{self.url}/", relative_url)
