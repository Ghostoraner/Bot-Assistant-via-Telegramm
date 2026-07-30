import asyncio
import html
import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Ключові слова для фільтрації під кожен напрямок
KEYWORDS_MAP: Dict[str, List[str]] = {
    "cpp": ["c++", "cpp", "embedded", "stm32", "microcontroller", "qt", "c language", "firmware", "arm", "esp32"],
    "mobile": ["flutter", "android", "ios", "react native", "swift", "kotlin", "mobile", "dart"],
    "python": ["python", "django", "fastapi", "flask", "aiogram", "asyncio", "pandas", "pytorch", "scikit"],
    "web": ["frontend", "backend", "fullstack", "react", "vue", "node", "javascript", "typescript", "html", "css",
            "php", "laravel"],
    "design": ["design", "ui", "ux", "figma", "photoshop", "illustrator", "дизайн", "логотип", "баннер"],
    "qa": ["qa", "testing", "tester", "selenium", "cypress", "тестирование", "тестировщик"],
    "devops": ["devops", "docker", "kubernetes", "k8s", "aws", "linux", "cicd", "ci/cd", "bash", "ansible"],
}


class FreelanceService:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
        }

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Універсальний завантажувач сторінок з таймаутом і залогованими помилками."""
        try:
            async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return await resp.text()
                logger.warning(f"Failed to fetch {url}, status code: {resp.status}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def _matches_category(self, text: str, category: str) -> bool:
        """Перевіряє, чи містить текст хоча б одне ключове слово заданої категорії."""
        if not category or category.lower() == "all":
            return True

        cat_key = category.lower().strip()

        # Знаходимо ключові слова або шукаємо прямо за назвою категорії
        keywords = KEYWORDS_MAP.get(cat_key, [cat_key])

        text_clean = html.unescape(text).lower()

        for kw in keywords:
            # Використовуємо регулярні вирази з \b, щоб 'c' не збігалося з кожним словом
            pattern = re.escape(kw)
            if re.search(r'\b' + pattern + r'\b', text_clean, re.IGNORECASE) or kw in text_clean:
                return True
        return False

    def _clean_text(self, text: str) -> str:
        """Декодує HTML-сутності та розчищає зайві пробіли."""
        if not text:
            return ""
        decoded = html.unescape(text)
        return " ".join(decoded.split())

    # ==========================================
    # 1. ТЕЛЕГРАМ-КАНАЛИ (Веб-парсер t.me/s/)
    # ==========================================
    async def parse_telegram_channel(self, session: aiohttp.ClientSession, channel_username: str, category: str) -> \
    List[Dict[str, str]]:
        jobs = []
        html_data = await self._fetch(session, f"https://t.me/s/{channel_username}")
        if html_data:
            soup = BeautifulSoup(html_data, "html.parser")
            posts = soup.select("div.tgme_widget_message")
            for post in posts[-10:]:
                text_elem = post.select_one("div.tgme_widget_message_text")
                link_elem = post.select_one("a.tgme_widget_message_date")
                if text_elem and link_elem:
                    full_text = self._clean_text(text_elem.text)
                    if self._matches_category(full_text, category):
                        title = full_text[:90] + "..." if len(full_text) > 90 else full_text
                        jobs.append({
                            "source": f"Telegram (@{channel_username})",
                            "title": title,
                            "price": "Див. опис у TG",
                            "link": link_elem.get("href", f"https://t.me/{channel_username}")
                        })
        return jobs

    # ==========================================
    # 2. УКРАЇНСЬКІ ТА БУДЬ-ЯКІ РЕГІОНАЛЬНІ БІРЖІ
    # ==========================================
    async def parse_freelancehunt(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        xml_data = await self._fetch(session, "https://freelancehunt.com/rss/projects")
        if xml_data:
            try:
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title = self._clean_text(item.find("title").text if item.find("title") is not None else "")
                    link = item.find("link").text if item.find("link") is not None else ""
                    if self._matches_category(title, category):
                        jobs.append({
                            "source": "Freelancehunt",
                            "title": title,
                            "price": "Договірна",
                            "link": link
                        })
            except Exception as e:
                logger.error(f"FH RSS parse error: {e}")
        return jobs

    async def parse_habr(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        html_data = await self._fetch(session, "https://freelance.habr.com/tasks")
        if html_data:
            soup = BeautifulSoup(html_data, "html.parser")
            for item in soup.select("li.content-list__item"):
                title_elem = item.select_one("div.task__title a")
                price_elem = item.select_one("span.count")
                if title_elem:
                    title = self._clean_text(title_elem.text)
                    if self._matches_category(title, category):
                        jobs.append({
                            "source": "Habr Freelance",
                            "title": title,
                            "price": self._clean_text(price_elem.text) if price_elem else "Договірна",
                            "link": f"https://freelance.habr.com{title_elem['href']}"
                        })
        return jobs

    async def parse_weblancer(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        html_data = await self._fetch(session, "https://www.weblancer.net/jobs/")
        if html_data:
            soup = BeautifulSoup(html_data, "html.parser")
            for row in soup.select("div.row.click_container-link"):
                title_elem = row.select_one("a.text-bold")
                price_elem = row.select_one("div.float-right")
                if title_elem:
                    title = self._clean_text(title_elem.text)
                    if self._matches_category(title, category):
                        jobs.append({
                            "source": "Weblancer",
                            "title": title,
                            "price": self._clean_text(price_elem.text) if price_elem else "Договірна",
                            "link": f"https://www.weblancer.net{title_elem['href']}"
                        })
        return jobs

    async def parse_freelance_ua(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        html_data = await self._fetch(session, "https://freelance.ua/orders/")
        if html_data:
            soup = BeautifulSoup(html_data, "html.parser")
            for item in soup.select("li.j-order"):
                title_elem = item.select_one("a.l-title")
                price_elem = item.select_one("span.l-price")
                if title_elem:
                    title = self._clean_text(title_elem.text)
                    if self._matches_category(title, category):
                        jobs.append({
                            "source": "Freelance.ua",
                            "title": title,
                            "price": self._clean_text(price_elem.text) if price_elem else "Договірна",
                            "link": f"https://freelance.ua{title_elem['href']}"
                        })
        return jobs

    async def parse_justfreelance(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        html_data = await self._fetch(session, "https://justfreelance.org/project")
        if html_data:
            soup = BeautifulSoup(html_data, "html.parser")
            for item in soup.select(".project-card"):
                title_elem = item.select_one(".project-title")
                price_elem = item.select_one(".project-price")
                link_elem = item.select_one("a")
                if title_elem and link_elem:
                    title = self._clean_text(title_elem.text)
                    if self._matches_category(title, category):
                        link = link_elem["href"]
                        jobs.append({
                            "source": "JustFreelance",
                            "title": title,
                            "price": self._clean_text(price_elem.text) if price_elem else "Договірна",
                            "link": link if link.startswith("http") else f"https://justfreelance.org{link}"
                        })
        return jobs

    # ==========================================
    # 3. МІЖНАРОДНІ API ТА RSS СТРІЧКИ
    # ==========================================
    async def parse_remoteok(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        try:
            async with session.get("https://remoteok.com/api", headers=self.headers,
                                   timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for item in data[1:]:
                        position = self._clean_text(item.get("position", ""))
                        tags = " ".join(item.get("tags", []))
                        search_text = f"{position} {tags}"

                        if self._matches_category(search_text, category):
                            jobs.append({
                                "source": "RemoteOK (Global)",
                                "title": f"{position} @ {self._clean_text(item.get('company', ''))}",
                                "price": item.get("salary", "Договірна"),
                                "link": item.get("url")
                            })
        except Exception as e:
            logger.error(f"RemoteOK API Error: {e}")
        return jobs

    async def parse_weworkremotely(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        xml_data = await self._fetch(session, "https://weworkremotely.com/remote-jobs.rss")
        if xml_data:
            try:
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title = self._clean_text(item.find("title").text if item.find("title") is not None else "")
                    link = item.find("link").text if item.find("link") is not None else ""
                    if self._matches_category(title, category):
                        jobs.append({
                            "source": "WeWorkRemotely",
                            "title": title,
                            "price": "Global/USD",
                            "link": link
                        })
            except Exception as e:
                logger.error(f"WeWorkRemotely RSS Error: {e}")
        return jobs

    async def parse_jobspresso(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, str]]:
        jobs = []
        xml_data = await self._fetch(session, "https://jobspresso.co/feed/")
        if xml_data:
            try:
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title = self._clean_text(item.find("title").text if item.find("title") is not None else "")
                    link = item.find("link").text if item.find("link") is not None else ""
                    if self._matches_category(title, category):
                        jobs.append({
                            "source": "Jobspresso",
                            "title": title,
                            "price": "Global/USD",
                            "link": link
                        })
            except Exception as e:
                logger.error(f"Jobspresso RSS Error: {e}")
        return jobs

    # ==========================================
    # 4. ГОЛОВНА ТОЧКА ВХОДУ (Запуск усього)
    # ==========================================
    async def get_jobs(self, category: str = "all") -> List[Dict[str, str]]:
        async with aiohttp.ClientSession() as session:
            tg_channels = [
                "findervc",
                "freelance_orders",
                "it_jobs",
                "python_job_feed",
                "perezagruzka_it",
                "job_freelance"
            ]

            tasks = [
                self.parse_freelancehunt(session, category),
                self.parse_habr(session, category),
                self.parse_weblancer(session, category),
                self.parse_freelance_ua(session, category),
                self.parse_justfreelance(session, category),
                self.parse_remoteok(session, category),
                self.parse_weworkremotely(session, category),
                self.parse_jobspresso(session, category),
            ]

            for ch in tg_channels:
                tasks.append(self.parse_telegram_channel(session, ch, category))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_jobs = []
            for res in results:
                if isinstance(res, list):
                    all_jobs.extend(res)
                elif isinstance(res, Exception):
                    logger.error(f"Task failed with error: {res}")

            # Обрізаємо результати до максимум 15 найсвіжіших вакансій
            return all_jobs[:15]