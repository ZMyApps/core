from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Config(ConfigBase):
    this_repo: str
    build_archive_repo: str
    ipa_archive_repo: str
    tweak_archive_repo: str
    apps: list[App]


class App(ConfigBase):
    name: str
    bundle_identifier: str
    tweaks: list[Tweak] = Field(default_factory=list)


class Tweak(ConfigBase):
    name: str
    deb_files: list[
        Annotated[
            CydiaRepoDebFile | GithubReleasesDebFile, Field(discriminator="source")
        ]
    ] = Field(default_factory=list)


class DebFileBase(ConfigBase):
    version: str = "latest"
    endswith: str | None = None
    use_version: bool = False


class CydiaRepoDebFile(DebFileBase):
    source: Literal["cydia_repo"] = "cydia_repo"
    repo: str
    package: str
    architecture: str


class GithubReleasesDebFile(DebFileBase):
    source: Literal["github_releases"] = "github_releases"
    repo: str
