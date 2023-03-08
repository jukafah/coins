import argparse
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prod', action='store_true')
    args = parser.parse_args()
    load_dotenv(f"solcoins/{'.env.dev' if not args.prod else '.env'}")
    from solcoins.bot import start
    start()
