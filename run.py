import os

from scraper import QuotesScraper


def get_main_dir_path():
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    path = get_main_dir_path()
    quotes_scraper = QuotesScraper(main_dir_path=path)
    quotes_scraper.run()
