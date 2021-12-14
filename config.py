import os

# OAuth token to tell twitch who you are (so you can unlock emotes).
# Take this from the network tab in a logged in twitch session
# You can find that by going to twitch, and then check for the
# Authorization header in the network tab. It will contain
# something like `Authorization: OAuth BLABLABLABLABLA`. The `BLABLABLABLABLA`
# is what you need. You can expose this via a environment variable called
# `TWITCH_OAUTH_TOKEN` or if you don't want to work with the environment
# variable, you can just set `oauth_token = "BLABLABLABLABLA"` here
oauth_token = os.environ.get('TWITCH_OAUTH_TOKEN')

# This one is hardcoded by twitch, and it should not be required to
# be changed.
# To confirm the correctness of this value, you can go to twitch.tv
# and look at the website source, search for 'clientId="' and the value
# right after that should match this value here
twitch_client_id = "kimne78kx3ncx6brgo4mv6wki5h1ko"

# Define channels in which you want which emotes to be unlocked
# note that the emotes have to be actually unlockable by channel points
twitch_channels = [
     {
        # The channel name
        "name": "nc_para_",

        # The emotes that should be unlocked for that channel
        "emotes": ["ncpara1Love", "ncpara1Foxy"],

        # The number of tries until the script gives up unlocking emotes.
        # This is only used when the 'Unlock a random Sub Emote' has to
        # be used.
        # Optional, defaults to 1
        "random_tries": 5,
    },
]
