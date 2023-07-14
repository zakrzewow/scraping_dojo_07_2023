import logging

import dotenv
import jsonlines
from playwright.sync_api import sync_playwright

from .browser_handler import BrowserHandler


class QuotesScraper:
    __slots__ = [
        "_logger",
        "_main_dir_path",
        "_proxy",
        "_input_url",
        "_output_file",
        "_quotes_list",
        "_proxy_settings",
    ]

    def __init__(self, main_dir_path) -> None:
        self._config_logger()
        self._logger.debug("QuotesScraper running...")
        self._main_dir_path = main_dir_path
        self._quotes_list = []
        self._load_env()
        self._prepare_proxy_settings()

    def _config_logger(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s [%(module)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def _load_env(self):
        env_dict = dotenv.dotenv_values(".env")
        self._proxy = env_dict["PROXY"]
        self._input_url = env_dict["INPUT_URL"]
        self._output_file = env_dict["OUTPUT_FILE"]
        self._logger.debug(".env loaded.")

    def _prepare_proxy_settings(self):
        user_pass, server = self._proxy.split("@")
        username, password = user_pass.split(":")
        self._proxy_settings = {
            "server": server,
            "username": username,
            "password": password,
        }

    def run(self):
        self._scrap_quotes()
        self._write_quotes_to_file()

    def _scrap_quotes(self):
        self._logger.debug("Scraping quotes...")
        with sync_playwright() as playwright:
            browser = BrowserHandler(playwright, self._input_url, self._proxy_settings)

            while True:
                quotes = browser.scrap_quotes_from_page()
                self._add_quotes_to_list(quotes)
                self._logger.debug(
                    f"Page {browser.page_idx}: scraped {len(quotes)} quotes"
                )
                if browser.has_next_page():
                    browser.go_next_page()
                else:
                    break

            browser.close()
        self._logger.debug("Quotes scraped.")

    def _add_quotes_to_list(self, quotes):
        self._quotes_list.extend(quotes)

    def _write_quotes_to_file(self):
        output_filepath = f"{self._main_dir_path}\{self._output_file}"
        with jsonlines.open(output_filepath, "w") as writer:
            writer.write_all(self._quotes_list)
        self._logger.debug(f"Quotes saved to file {output_filepath}")
