
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def get_recently_played_games():
    params = urlencode({
        "key": os.environ["STEAM_API_KEY"],
        "steamid": os.environ["STEAM_ID"],
        "count": 10,
    })

    url = (
        "https://api.steampowered.com/"
        "IPlayerService/GetRecentlyPlayedGames/v1/"
        f"?{params}"
    )

    request = Request(
        url,
        headers={"User-Agent": "SteamProfileUpdater/1.0"}
    )

    with urlopen(request, timeout=30) as response:
        result = json.load(response)

    if "response" not in result:
        raise RuntimeError("Invalid Steam API response")

    games = result["response"].get("games", [])

    return [
        {
            "appid": game["appid"],
            "name": game["name"],
            "playtime_2weeks": game.get("playtime_2weeks", 0),
            "playtime_forever": game.get("playtime_forever", 0),
        }
        for game in games
    ]


def main():
    games = get_recently_played_games()

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "games": games,
    }

    output = Path("data/games.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    temp = output.with_suffix(".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp.replace(output)

    print(f"Updated {len(games)} games.")


if __name__ == "__main__":
    main()
