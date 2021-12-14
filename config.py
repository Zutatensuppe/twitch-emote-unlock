import os
import toml

_config = toml.load(os.environ.get("TWITCH_EMOTE_UNLOCK_CONFIG") or "config.toml")

oauth_token = _config["oauth_token"] or os.environ.get("TWITCH_OAUTH_TOKEN")
twitch_client_id = _config["twitch_client_id"]
twitch_channels = _config["twitch_channels"]
