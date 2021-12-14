import requests
import hashlib
import uuid
import config

def gen_transaction_id():
    m = hashlib.md5()
    m.update(f"{uuid.uuid1()}".encode("UTF-8"))
    return m.hexdigest()


def post(data):
    return requests.post(
        "https://gql.twitch.tv/gql#origin=twilight",
        headers={
            "Client-Id": config.twitch_client_id,
            "Authorization": f"OAuth {config.oauth_token}",
        },
        json=data,
    )


def unlock_chosen_emote(channel_id, unlock_cost, emote_id):
    data = [
        {
            "operationName": "UnlockChosenSubscriberEmote",
            "variables": {
                "input": {
                    "channelID": channel_id,
                    "emoteID": emote_id,
                    "cost": unlock_cost,
                    "transactionID": gen_transaction_id(),
                },
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "1106d2d730a63370bb95f2b27ab098d64efb4482cc2e1551210fc0fce09c3062",
                },
            },
        }
    ]

    res = post(data)
    resjson = res.json()
    if resjson[0]["data"]["unlockChosenSubscriberEmote"]["error"]:
        print(repr(resjson))
        return False
    else:
        return True


def unlock_random_emote(channel_id, unlock_cost):
    data = [
        {
            "operationName": "UnlockRandomSubscriberEmote",
            "variables": {
                "input": {
                    "channelID": channel_id,
                    "cost": unlock_cost,
                    "transactionID": gen_transaction_id(),
                }
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "f548e89966b21d0094f3dc35233232eb6ec76d63e02594c8a494407712a85350",
                }
            },
        }
    ]
    res = post(data)
    resjson = res.json()
    if resjson[0]["data"]["unlockRandomSubscriberEmote"]["error"]:
        print(repr(resjson))
        return False
    else:
        return True


def get_user_emotes_info():
    data = [
        {
            "operationName": "UserEmotes",
            "variables": {"withOwner": True},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "7c15c1c83a9cf574aa202ddf6f40594ff75b2715746d98a20eea068e0c1179b7",
                }
            },
        }
    ]
    res = post(data)
    return res.json()


def get_channel_points_context(channel_name):
    data = [
        {
            "operationName": "ChannelPointsContext",
            "variables": {
                "channelLogin": channel_name,
                "includeGoalTypes": ["CREATOR", "BOOST"],
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "1530a003a7d374b0380b79db0be0534f30ff46e61cffa2bc0e2468a909fbc024",
                }
            },
        },
    ]
    res = post(data)
    return res.json()


def extract_unlock_emote_costs(channel_points_context):
    item = channel_points_context[0]
    settings = item["data"]["community"]["channel"]["communityPointsSettings"]
    automatic = settings["automaticRewards"]

    chosenCost = 0
    randomCost = 0
    for item in automatic:
        if item["type"] == "CHOSEN_SUB_EMOTE_UNLOCK" and item["isEnabled"]:
            chosenCost = item["defaultCost"] or item["minimumCost"]
        elif item["type"] == "RANDOM_SUB_EMOTE_UNLOCK" and item["isEnabled"]:
            randomCost = item["defaultCost"] or item["minimumCost"]

    return {
        "chosenCost": chosenCost,
        "randomCost": randomCost,
    }


def extract_channel_id(channel_points_context):
    item = channel_points_context[0]
    return item["data"]["community"]["id"]


def emotes_diff(channel_points_context, user_emotes_info, desired_emotes: set):
    channel_emotes_map = dict()
    for emoteVariant in channel_points_context[0]['data']['community']['channel']['communityPointsSettings']["emoteVariants"]:
        if emoteVariant["isUnlockable"]:
            channel_emotes_map[emoteVariant["emote"]["token"]] = emoteVariant["emote"]["id"]

    user_emotes_map = dict()
    for emoteSet in user_emotes_info[0]["data"]["currentUser"]["emoteSets"]:
        for emote in emoteSet["emotes"]:
            user_emotes_map[emote["token"]] = emote["id"]

    missing_ids = []
    for token in desired_emotes:
        if not user_emotes_map.get(token) and channel_emotes_map.get(token):
            missing_ids.append(channel_emotes_map.get(token))
    return missing_ids


def handle_channel(channel):
    channel_emotes = channel["emotes"]
    channel_name = channel["name"]
    print(f"Handling channel {channel_name}")
    if not channel_emotes:
        print(f"✓ User does not desire any emotes")
        return

    channel_points_context = get_channel_points_context(channel_name)
    channel_id = extract_channel_id(channel_points_context)
    if not channel_id:
        print("✖ Unable to extract channel id")
        return
    print(f"Extracted channel id {channel_id}")

    user_emotes_info = get_user_emotes_info()
    diff = emotes_diff(channel_points_context, user_emotes_info, channel_emotes)
    if not diff:
        print(f"✓ User already has all desired emotes ({', '.join(channel_emotes)})")
        return

    costs = extract_unlock_emote_costs(channel_points_context)
    if costs["chosenCost"]:
        # unlock via 'chosen' method
        print(f"🪙  Price to unlock CHOSEN emote: {costs['chosenCost']}")
        while diff:
            unlocked = unlock_chosen_emote(channel_id, costs["chosenCost"], diff[0])
            if not unlocked:
                print("✖ Error when trying to unlock chosen emote")
                return
            print("🔓 Unlocked a chosen emote")
            user_emotes_info = get_user_emotes_info()
            diff = emotes_diff(channel_points_context, user_emotes_info, channel_emotes)
        print(f"✓ User now has all desired emotes ({', '.join(channel_emotes)})")
    elif costs["randomCost"]:
        # unlock via 'random' method
        print(f"🪙  Price to unlock RANDOM emote: {costs['randomCost']}")
        random_tries = channel.get("random_tries", 1)
        while random_tries > 0:
            unlocked = unlock_random_emote(channel_id, costs["randomCost"])
            if not unlocked:
                print("✖ Error when trying to unlock random emote")
                return

            print("🔓 Unlocked a random emote")
            user_emotes_info = get_user_emotes_info()
            diff = emotes_diff(channel_points_context, user_emotes_info, channel_emotes)
            if not diff:
                print(f"✓ User now has all desired emotes ({', '.join(channel_emotes)})")
                return
            random_tries -= 1
    else:
        print("✖ The channel doesn't allow unlocking emotes")
        return

def run():
    if not config.twitch_channels:
        print("No twitch channels are configured (check config.py)")
    for channel in config.twitch_channels:
        handle_channel(channel)


run()

# TODO: replace this with a better solution ^_^
#       we dont always want to press buttons!
input("\nPress ENTER to continue.")
