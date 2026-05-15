#!/usr/bin/env -S uv run

import asyncio
import subprocess
from time import time

import httpx

from shared import a_newer_than_b, confirm
from shared.config import config
from shared.repo import decrypted_latest_repo, tweaked_latest_repo

LINE_SEPARATOR = "---------------------------------------------------------------------------------------------------"


async def lookup_appstore(client: httpx.AsyncClient, bundle_identifier: str):
    response = await client.get(
        f"https://itunes.apple.com/lookup?bundleId={bundle_identifier}&cacheBusting={time()}"
    )
    data = response.json()
    return (data["results"][0]["version"], data["results"][0]["trackViewUrl"])


async def main():
    print("Fetching decryptedlatest.json and tweakedlatest.json")
    await asyncio.gather(
        asyncio.to_thread(decrypted_latest_repo.fetch),
        asyncio.to_thread(tweaked_latest_repo.fetch),
    )

    print(LINE_SEPARATOR)
    print(
        f"{'name':<14}",
        f"{'appstore':<9}",
        f"{'decrypted':<9}",
        f"{'': <2}",
        f"{'tweaked':<9}",
        f"{'': <2}",
        f"{'link'}",
    )
    print(LINE_SEPARATOR)

    async with httpx.AsyncClient() as client:
        appstore_results = await asyncio.gather(
            *[lookup_appstore(client, app.bundle_identifier) for app in config.apps]
        )

    outdated_apps: list[tuple[str, str]] = []
    for app, (appstore_version, appstore_link) in zip(config.apps, appstore_results):
        decrypted_app = decrypted_latest_repo.get_app_latest(
            bundle_identifier=app.bundle_identifier
        )
        decrypted_version = decrypted_app.version if decrypted_app else ""
        tweaked_app = tweaked_latest_repo.get_app_latest(
            bundle_identifier=app.bundle_identifier
        )
        tweaked_version = tweaked_app.version.split("_")[0] if tweaked_app else ""
        decrypted_outdated = ""
        if (
            appstore_version
            and decrypted_version
            and app.name not in ["Apollo"]
            and a_newer_than_b(appstore_version, decrypted_version)
        ):
            decrypted_outdated = "✓"
            outdated_apps.append((app.name, appstore_link))
        tweaked_outdated = ""
        if (
            appstore_version
            and tweaked_version
            and app.name not in ["Apollo"]
            and a_newer_than_b(appstore_version, tweaked_version)
        ):
            tweaked_outdated = "✓"

        print(
            f"{app.name:<14}",
            f"{appstore_version:<9}",
            f"{decrypted_version:<9}",
            f"{decrypted_outdated: <2}",
            f"{tweaked_version:<9}",
            f"{tweaked_outdated: <2}",
            f"{appstore_link}",
        )
    print(LINE_SEPARATOR)
    for outdated_app, outdated_link in outdated_apps:
        if confirm(prompt=f"Open Telegram for {outdated_app}'s link", default=True):
            telegram_bot = (
                "FastDecryptBot"
                if outdated_app in ["Instagram", "TikTok"]
                else "eeveedecrypterbot"
            )
            telegram_link = f"tg://resolve?domain={telegram_bot}&text={outdated_link}"
            subprocess.run(["open", telegram_link], check=True)


if __name__ == "__main__":
    asyncio.run(main())
