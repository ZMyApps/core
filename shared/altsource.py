from pydantic import BaseModel, ConfigDict, Field


class AltSourceBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AltSourceApp(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(frozen=True)
    bundleIdentifier: str = Field(frozen=True)
    version: str = Field(frozen=True)
    localizedDescription: str = Field(frozen=True)
    downloadURL: str = Field(frozen=True)
    iconURL: str = Field(frozen=True)
    versionDate: str = Field(frozen=True)
    size: int = Field(frozen=True)

    # for script usage only
    asset_id: str | None = Field(default=None, frozen=False)


class AltSourceRepo(AltSourceBase):
    name: str
    identifier: str
    iconURL: str
    apps: list[AltSourceApp]
