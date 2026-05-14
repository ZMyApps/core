from pydantic import BaseModel, ConfigDict


class AltSourceBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AltSourceApp(AltSourceBase):
    name: str
    bundleIdentifier: str
    version: str
    localizedDescription: str
    downloadURL: str
    iconURL: str
    versionDate: str
    size: int


class AltSourceRepo(AltSourceBase):
    name: str
    identifier: str
    iconURL: str
    apps: list[AltSourceApp]
