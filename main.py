import sys
import asyncio
import argparse
import logging
import os
from pathlib import Path
from typing import Optional

from opentele.td import TDesktop
from opentele.api import UseCurrentSession
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Configure the event loop policy to avoid issues with ProactorEventLoop on Windows
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_tdesktop_client(tdata_folder: Path) -> Optional[TDesktop]:
    """
    Loads the TDesktop client from the tdata folder.

    :param tdata_folder: Path to the tdata folder.
    :return: Loaded TDesktop client or None if failed.
    """
    logging.info(f"Loading TDesktop client from folder: {tdata_folder}")

    try:
        tdesktop_client = TDesktop(str(tdata_folder))
        if not tdesktop_client.isLoaded():
            logging.warning("No accounts loaded. Please check the tdata folder.")
            return None

        logging.info(f"TDesktop client loaded successfully. Accounts loaded: {len(tdesktop_client.accounts)}")
        return tdesktop_client

    except Exception as e:
        logging.error(f"Error loading TDesktop client: {e}", exc_info=True)
        return None


async def convert_to_telethon_session(tdesktop_client: TDesktop, session_file: Path) -> Optional[TelegramClient]:
    """
    Converts the TDesktop session to a Telethon session using the current session.

    :param tdesktop_client: Loaded TDesktop client.
    :param session_file: Path to save the Telethon session file.
    :return: Initialized Telethon client or None if failed.
    """
    try:
        logging.info("Converting TDesktop session to Telethon session using the current session...")

        client = await tdesktop_client.ToTelethon(
            session=str(session_file),
            flag=UseCurrentSession
        )

        await client.connect()

        if not await client.is_user_authorized():
            logging.warning("Client is not authorized.")
            return None

        me = await client.get_me()
        logging.info(f"Connected user: {me.first_name} (ID: {me.id})")

        if not session_file.exists():
            logging.error(f"Failed to save the session file: {session_file}")
            return None

        logging.info(f"Session file saved successfully: {session_file}")
        return client

    except SessionPasswordNeededError:
        logging.error("Two-factor authentication is enabled. Please disable it and try again.")
        return None

    except Exception as e:
        logging.error(f"Error converting to Telethon session: {e}", exc_info=True)
        return None


def check_duplicate_session(session_path: Path) -> bool:
    """
    Checks if a session file with the same name already exists.

    :param session_path: Path to the session file.
    :return: True if the file already exists, False otherwise.
    """
    if session_path.exists():
        logging.warning(f"Session file already exists: {session_path}")
        return True
    return False


async def process_tdata_folder(tdata_folder: Path, identifier: str, output_directory: Path):
    """
    Processes a single tdata folder and performs the conversion to Telethon.

    :param tdata_folder: Path to the tdata folder.
    :param identifier: Name or number associated with the session.
    :param output_directory: Directory where session files will be saved.
    """
    session_file = output_directory / f"{identifier}.session"

    if check_duplicate_session(session_file):
        logging.info(f"Session file '{session_file}' already exists. Please check and remove if necessary.")
        return

    tdesktop_client = load_tdesktop_client(tdata_folder)
    if tdesktop_client is None:
        logging.error("Failed to load TDesktop client. Please check the tdata folder and try again.")
        return

    client = None
    try:
        client = await convert_to_telethon_session(tdesktop_client, session_file)
        if client is None:
            logging.error("Failed to convert to Telethon session.")
            return

        logging.info(f"Processing for '{identifier}' completed successfully.")

    finally:
        if client:
            await client.disconnect()


async def main():
    parser = argparse.ArgumentParser(description='Convert TDesktop sessions to Telethon sessions.')
    parser.add_argument('directory', help='Directory containing one or multiple tdata folders.')
    parser.add_argument('--output', help='Directory where session files will be saved.', default='output')
    args = parser.parse_args()

    base_directory = Path(args.directory)
    output_directory = Path(args.output)

    if not base_directory.exists():
        logging.error(f"The specified directory does not exist: {base_directory}")
        sys.exit(1)

    # Ensure the output directory exists
    output_directory.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory is set to: {output_directory}")

    tasks = []

    # Check if it's a single tdata folder or a directory containing multiple tdata folders
    if (base_directory / "tdata").exists():
        # Single tdata folder
        identifier = base_directory.name
        tasks.append(process_tdata_folder(base_directory / "tdata", identifier, output_directory))
    else:
        # Directory containing multiple tdata folders
        for dir_name in os.listdir(base_directory):
            tdata_folder = base_directory / dir_name / "tdata"
            if tdata_folder.exists():
                tasks.append(process_tdata_folder(tdata_folder, dir_name, output_directory))

    if tasks:
        await asyncio.gather(*tasks)
    else:
        logging.warning("No tdata folders found in the specified directory.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
