import logging
import re
import asyncio
from datetime import datetime

from aiohttp import ClientTimeout

_LOGGER = logging.getLogger(__name__)


class BazosApi:
    def __init__(self, session):
        self._session = session
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    # -------------------------
    # PUBLIC API (ASYNC)
    # -------------------------
    async def fetch(self, url: str):
        offset = 0
        all_items = []
        seen = set()

        while True:
            _LOGGER.debug("url: %s", url)
            _LOGGER.debug("offset: %d", offset)

            pagedurl = self._getpagedurl(url, offset)

            html = await self._get(pagedurl)

            blocks = self._extract_blocks(html)

            _LOGGER.debug("Found blocks: %s", len(blocks))

            if not blocks:
                break

            new_count = 0

            for b in blocks:
                link = self._extract_link(b)
                item_id = self._extract_id(link)
                price = self._extract_price(b)

                if not item_id:
                    continue

                if item_id in seen:
                    continue

                seen.add(item_id)
                new_count += 1

                title = self._extract_title(b)
                date = self._extract_date(b)

                _LOGGER.info("New item: %s, Title: %s, Link: %s, Date: %s, Price: %d", item_id, title, link, date, price)

                all_items.append(
                    {
                        "id": item_id,
                        "title": title,
                        "link": link,
                        "date": date,
                        "price": price,
                    }
                )

            _LOGGER.debug(
                "Page offset=%s new=%s total=%s",
                offset,
                new_count,
                len(all_items),
            )

            # pagination stop condition
            if len(blocks) < 20:
                break

            offset += 20

            await asyncio.sleep(0.5)

        _LOGGER.debug("Total unique items: %s", len(all_items))
        return {"items": all_items}

    # -------------------------
    # HTTP (ASYNC)
    # -------------------------
    async def _get(self, url: str) -> str:
        timeout = ClientTimeout(total=10)

        async with self._session.get(
            url,
            headers=self._headers,
            timeout=timeout,
        ) as resp:
            resp.raise_for_status()
            return await resp.text()

    # -------------------------
    # BLOCK EXTRACTION
    # -------------------------
    def _extract_blocks(self, html: str):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        return soup.select("div.inzeraty.inzeratyflex")

    # -------------------------
    # LINK EXTRACTION
    # -------------------------
    def _extract_link(self, block):
        tag = block.select_one(".inzeratynadpis a")
        if tag and tag.get("href"):
            return tag.get("href")

        tag = block.select_one("a[href*='inzerat']")
        if tag and tag.get("href"):
            return tag.get("href")

        tag = block.find("a")
        if tag and tag.get("href"):
            return tag.get("href")

        return None

    # -------------------------
    # ID EXTRACTION
    # -------------------------
    def _extract_id(self, link: str):
        if not link:
            return None

        match = re.search(r"/(\d+)\.php", link)
        if match:
            return match.group(1)

        match = re.search(r"/(\d{6,})", link)
        if match:
            return match.group(1)

        return None

    # -------------------------
    # TITLE EXTRACTION
    # -------------------------
    def _extract_title(self, block):
        tag = block.select_one(".inzeratynadpis a")
        if tag:
            return tag.get_text(strip=True)

        tag = block.find("h2")
        if tag:
            return tag.get_text(strip=True)

        text = block.get_text(" ", strip=True)
        return text[:120] if text else ""

    # -------------------------
    # PRICE EXTRACTION
    # -------------------------
    def _extract_price(self, block):
        tag = block.select_one(".inzeratycena")
        if tag:
            text = tag.get_text(strip=True)
            number = re.sub(r"[^\d]", "", text)
            return int(number) if number else None

    # -------------------------
    # DATE EXTRACTION
    # -------------------------
    def _extract_date(self, block):
        text = block.get_text(" ", strip=True)

        match = re.search(r"\[(\d{1,2})\.(\d{1,2})\.\s*(\d{4})\]", text)

        if not match:
            return None

        d, m, y = map(int, match.groups())

        try:
            return datetime(y, m, d).date()
        except ValueError:
            return None

    def _getpagedurl(self, url: str, offset: int):
        return f"{url}&crz={offset}"
