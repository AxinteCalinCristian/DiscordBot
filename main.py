from decouple import config
from core import Core


def main():
    token = config('DISCORD_TOKEN')
    google_api_key = str(config('GOOGLE_API_TOKEN'))
    core_bot = Core(token, google_api_key)

    core_bot.runBot()


if __name__ == "__main__":
    main()
