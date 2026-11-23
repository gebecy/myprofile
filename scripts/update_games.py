
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen,HTTPError

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
    api_key = os.environ.get("STEAM_API_KEY", "")
    steam_id = os.environ.get("STEAM_ID", "")

    print(f"API Key exists: {bool(api_key)}")
    print(f"Steam ID exists: {bool(steam_id)}")
    print(f"Steam ID length: {len(steam_id)}")
    print(f"Steam ID format: {steam_id.isdigit()}")
    
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)

    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")

        print(f"Steam API HTTP Error: {e.code}")
        print(f"Response body: {error_body}")

        raise

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
