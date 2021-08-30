from decouple import config
from core import Core


def main():
    token = config('TOKEN')
    core_bot = Core(token)

    core_bot.runBot()


if __name__ == "__main__":
    main()
