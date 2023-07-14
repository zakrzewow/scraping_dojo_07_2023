from typing import List, Dict

from playwright.sync_api import Playwright


class BrowserHandler:
    __slots__ = ["_browser", "page_idx", "_page"]

    def __init__(
            self, playwright: Playwright, input_url: str, proxy_settings: dict
    ) -> None:
        self._browser = self._get_browser(playwright, proxy_settings)
        self.page_idx = 1
        self._page = self._browser.new_page()
        self._page.goto(input_url)

    def _get_browser(self, playwright: Playwright, proxy_settings: dict):
        return playwright.chromium.launch(slow_mo=100, proxy=proxy_settings)

    def scrap_quotes_from_page(self) -> List[Dict]:
        self._wait_for_quotes()
        return self._read_quotes()

    def _wait_for_quotes(self):
        # all quotes appear at the same time
        self._page.wait_for_selector(".quote")

    def _read_quotes(self) -> List[Dict]:
        quotes = []
        for quote in self._page.locator(".quote").all():
            quote_attrs = self._get_quote_attrs(quote)
            quotes.append(quote_attrs)
        return quotes

    def _get_quote_attrs(self, quote) -> Dict[str, str]:
        text = quote.locator(".text").text_content()
        author = quote.locator(".author").text_content()
        tags = [tag.text_content() for tag in quote.locator(".tag").all()]
        text = text.strip("“”")
        return {"text": text, "by": author, "tags": tags}

    def has_next_page(self) -> bool:
        return self._page.locator(".pager > .next > a").is_visible()

    def go_next_page(self):
        self.page_idx += 1
        self._page.locator(".pager > .next > a").click()
        self._page.wait_for_load_state()

    def close(self):
        self._browser.close()
