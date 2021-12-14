# twitch-emote-unlock

Tries to unlock the configured emotes in the configured channels
by using twitch's 'Choose an Emote to Unlock' and 
'Unlock a Random Sub Emote' functionality.

It may eat up your channel points :)

## Usage

1. Copy `config.example.toml` to `config.toml` and adjust as desired.
2. Install [python](https://www.python.org/downloads/)
3. Install [poetry](https://python-poetry.org/)
4. Run in a shell to install dependencies:
    poetry install
5. Run in a shell to launch the script:
    poetry run python run.py


**Alternatively you can use a pre built executable file:** 
1. Download a release archive from the releases [releases](https://github.com/Zutatensuppe/twitch-emote-unlock/releases/latest) page
2. Extract the archive and adjust the `config.toml` file as desired.
3. Launch the executable :)
