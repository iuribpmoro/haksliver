# HakSliver

A custom sliver client that will send discord notifications upon new beacons / sessions that check in. Can either be run with a config file (that will be reloaded after `sleep` number of seconds, except for the `sliver_config` as the intial connection is used for all checks).

Started as a fork of https://github.com/ezra-buckingham/sally-the-sliver-siren/tree/main.

## Usage

To use haksliver, first install all dependencies using `pip`:

```bash
pip3 install -r requirements.txt
```

Once all dependencies are installed, you can then run the python script (which will run continuously).

```
usage: haksliver.py [-h] [-c CONFIG] [-S SLIVER_CONFIG] [-u DISCORD_URL] [-s SLEEP]

Custom Sliver client that will will emit events and send webhook notifications when new beacons / sessions check in.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to haksliver config file (which will immediately take effect as changes to haksliver)
  -S SLIVER_CONFIG, --sliver_config SLIVER_CONFIG
                        Path to the sliver config to connect with
  -u DISCORD_URL, --discord_url DISCORD_URL
                        Discord URL to send notifications to
  -s SLEEP, --sleep SLEEP
                        Sleep time in between checking for changes in beacons / sessions
```

### Usage with Command Line

If you want to run the command using only the command line arguments, a sample command would look like the following:

```bash
python3 ./haksliver.py -S /path/to/sliver-config.conf -s 10 -u https://discord.com
```

### Usage with Config File

If you choose to run the custom client as a service on the host, the most convenient way to manage the arguments is via a configuration file that will propogate changes into the running service every `sleep` number of seconds.

```bash
python3 ./haksliver.py -c /path/to/haksliver-config.conf
```

For convenience, there is a `config_example.yml` file included in the repo (default search location for haksliver is `./config.yml`).

## Running Continuously

Since this is just a python script, you can choose to install it as a service and run it continuously that way OR you can use a `tmux` / `screen` session to run it. If you want to go the service route, I have an example [service file](./service/haksliver.service) included in this repo.
