from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class GithubRepo(BaseModel):
    owner: str
    repo: str

    def __init__(self, full_name: str | None, **data: Any) -> None:
        if full_name is not None:
            if data:
                raise ValueError("GithubRepo full_name or **data not both")
            owner, repo = full_name.split("/", 1)
            data = {"owner": owner, "repo": repo}
        super().__init__(**data)

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"

    def __str__(self) -> str:
        return self.full_name


class Config(ConfigBase):
    local_username: str
    this_repo: GithubRepo
    files_repo: GithubRepo
    files_repo_json_tag: str
    build_archive_repo: GithubRepo
    ipa_archive_repo: GithubRepo
    apps: list[App]


class App(ConfigBase):
    name: str
    bundle_identifier: str
    tweaks: list[Tweak] = Field(default_factory=list)


class Tweak(ConfigBase):
    name: str
    note: str | None = None
    deb_files: list[
        Annotated[
            CydiaRepoDebFile | GithubReleasesDebFile, Field(discriminator="source")
        ]
    ] = Field(default_factory=list)


class DebFileBase(ConfigBase):
    endswith: str | None = None
    use_version: bool = False


class CydiaRepoDebFile(DebFileBase):
    source: Literal["cydia_repo"] = "cydia_repo"
    repo: str
    package: str
    architecture: str
    version: str = "latest"


class GithubReleasesDebFile(DebFileBase):
    source: Literal["github_releases"] = "github_releases"
    repo: GithubRepo
    tag: str = "latest"
