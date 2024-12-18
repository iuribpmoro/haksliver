#!/usr/bin/env python3

import asyncio
from pathlib import Path
from time import sleep
import argparse
import requests
from sliver import *
import yaml

async def main():
    parser = argparse.ArgumentParser(description='Custom Sliver client that will emit events and send webhook notifications when new beacons/sessions check in.')
    parser.add_argument('-c', '--config', type=Path, help='Path to haksliver config file (which will immediately take effect as changes to haksliver)')
    parser.add_argument('-S', '--sliver_config', default=None, type=Path, help='Path to the sliver config to connect with')
    parser.add_argument('-u', '--discord_url', default=None, type=str, help='Discord WebHook to send notifications to')
    parser.add_argument('-s', '--sleep', type=int, default=10, help='Sleep time in between checking for changes in beacons/sessions')

    args = parser.parse_args()
    haksliver_config = args.config
    sliver_config = args.sliver_config
    discord_url = args.discord_url
    sleep_time = args.sleep

    # Flag to represent if we are using a config file
    using_config = False

    if haksliver_config and not sliver_config and not discord_url:
        using_config = True
        sliver_config, discord_url, sleep_time = read_config(haksliver_config)

    sliver_config = Path(sliver_config)  # Convert to Path object
    if not sliver_config.exists():
        print('[X] Sliver config not found at location provided')
        exit(1)

    config = SliverClientConfig.parse_config_file(sliver_config)
    client = SliverClient(config)
    print('[*] Connecting to Sliver Server...')
    await client.connect()
    print('[*] Connected to Sliver Server!')

    print('[*] Getting current Sliver beacons')
    original_beacons = await client.beacons()
    print('[*] Getting current Sliver sessions')
    original_sessions = await client.sessions()

    while True:
        current_beacons = await client.beacons()
        difference_in_beacons = extract_uuid(
            current_beacons) - extract_uuid(original_beacons)

        current_sessions = await client.sessions()
        difference_in_sessions = extract_uuid(
            current_sessions) - extract_uuid(original_sessions)

        if len(difference_in_beacons) > 0:
            print('[*] Found new beacons')
            original_beacons = current_beacons

            for new_beacon in difference_in_beacons:
                new_beacon_data = [
                    selected_beacon for selected_beacon in current_beacons if selected_beacon.ID == new_beacon]
                new_beacon_data = new_beacon_data[0]
                post_data = generate_discord_message(new_beacon_data, 'beacon')

                print(f'[*] Sending message about beacon {new_beacon}')
                try:
                    resp = requests.post(discord_url, json=post_data)
                    print(f'[*] Sent message: HTTP ({resp.status_code})')
                except:
                    print(f'[X] Something went wrong when sending webhook message, check the URL used')

        else:
            print('[*] No new beacons found')

        if len(difference_in_sessions) > 0:
            print('[*] Found new sessions')
            original_sessions = current_sessions

            for new_session in difference_in_sessions:
                new_session_data = [
                    selected_session for selected_session in current_sessions if selected_session.ID == new_session]
                new_session_data = new_session_data[0]
                post_data = generate_discord_message(new_session_data, 'session')

                print(f'[*] Sending message about session {new_session}')
                try:
                    resp = requests.post(discord_url, json=post_data)
                    print(f'[*] Sent message: HTTP ({resp.status_code})')
                except:
                    print(f'[X] Something went wrong when sending webhook message, check the URL used')

        else:
            print('[*] No new sessions found')

        print(f'[*] Sleeping for {sleep_time} seconds')
        sleep(sleep_time)

        # Get new config values
        if using_config:
            sliver_config, discord_url, sleep_time = read_config(haksliver_config)
            sliver_config = Path(sliver_config)  # Convert to Path again

def read_config(config_path):
    config_file = Path(config_path).read_text()
    config_file_yaml = yaml.safe_load(config_file)

    return config_file_yaml['sliver_config'], config_file_yaml['discord_url'], config_file_yaml['sleep_time']


def extract_uuid(beacon_list):
    beacon_uuids = [beacon.ID for beacon in beacon_list]

    return set(beacon_uuids)


def generate_discord_message(data, type='beacon'):
    header_text = '🚨  New Sliver '

    if type == 'beacon':
        header_text += 'Beacon'
    elif type == 'session':
        header_text += 'Session'
    else:
        header_text += 'Event'

    post_data = {
        "content": f"{header_text}!\n\n ```{data}```"
    }

    return post_data


if __name__ == '__main__':
    asyncio.run(main())  # Use asyncio.run() instead of get_event_loop()
