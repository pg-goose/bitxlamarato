import argparse
import requests

SOURCE_URL = "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"


def main():


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", help="Year to download", type=int)
    parser.add_argument("-m", "--month", help="Month to download", type=int)
    args = parser.parse_args()
    main()