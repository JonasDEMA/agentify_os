"""
Company Scraper - Extract information from company websites
"""

import asyncio
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser

from config import settings


class CompanyScraper:
    """Scrape company websites for information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent
        })
        self.last_request_time = {}
        self.robots_parsers = {}
    
    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        if not settings.respect_robots_txt:
            return True
        
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Get or create robots.txt parser for this domain
        if domain not in self.robots_parsers:
            robots_url = f"{domain}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_parsers[domain] = rp
            except:
                # If robots.txt can't be read, allow by default
                return True
        
        return self.robots_parsers[domain].can_fetch(settings.user_agent, url)
    
    def _rate_limit(self, domain: str):
        """Apply rate limiting per domain"""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < settings.min_request_delay:
                time.sleep(settings.min_request_delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        # TODO: Implement page fetching
        # - Check robots.txt
        # - Apply rate limiting
        # - Handle errors gracefully
        # - Return HTML content
        
        if not self._can_fetch(url):
            print(f"⚠️  Blocked by robots.txt: {url}")
            return None
        
        parsed = urlparse(url)
        domain = parsed.netloc
        self._rate_limit(domain)
        
        try:
            response = self.session.get(
                url,
                timeout=settings.request_timeout
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML"""
        # TODO: Implement text extraction
        # - Remove scripts, styles
        # - Extract main content
        # - Clean whitespace
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def find_relevant_pages(self, base_url: str, html: str) -> Dict[str, str]:
        """Find relevant pages (About, Team, News, etc.)"""
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        soup = BeautifulSoup(html, 'html.parser')
        pages = {}

        # Keywords for different page types
        keywords = {
            'about': ['about', 'über uns', 'ueber uns', 'company', 'unternehmen'],
            'team': ['team', 'management', 'geschäftsführung', 'geschaeftsfuehrung', 'vorstand'],
            'news': ['news', 'aktuelles', 'presse', 'press', 'blog']
        }

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()

            for page_type, kws in keywords.items():
                if page_type not in pages:
                    for kw in kws:
                        if kw in href or kw in text:
                            full_url = urljoin(base_url, link['href'])
                            pages[page_type] = full_url
                            break

        return pages

    async def scrape_company(
        self,
        company_name: str,
        website: str,
        fields: list
    ) -> Dict[str, Any]:
        """Scrape company website for specified fields"""
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"🔍 Scraping {company_name} - {website}")

        result = {
            "company_name": company_name,
            "website": website,
            "extracted_data": {},
            "sources": [],
            "confidence": 0.0,
            "status": "success"
        }

        try:
            # Normalize URL
            if not website.startswith(('http://', 'https://')):
                website = f'https://{website}'

            # Fetch main page
            logger.info(f"📄 Fetching main page: {website}")
            html = self.fetch_page(website)

            if not html:
                logger.warning(f"⚠️  Could not fetch {website}")
                result["status"] = "failed"
                result["error"] = "Could not fetch website"
                return result

            # Extract text from main page
            main_text = self.extract_text(html)
            logger.info(f"✅ Extracted {len(main_text)} characters from main page")

            # Find relevant pages
            relevant_pages = self.find_relevant_pages(website, html)
            logger.info(f"🔗 Found relevant pages: {list(relevant_pages.keys())}")

            # Collect all text
            all_text = f"Main Page:\n{main_text}\n\n"
            result["sources"].append(website)

            # Fetch relevant pages
            for page_type, url in relevant_pages.items():
                logger.info(f"📄 Fetching {page_type} page: {url}")
                page_html = self.fetch_page(url)
                if page_html:
                    page_text = self.extract_text(page_html)
                    all_text += f"{page_type.title()} Page:\n{page_text}\n\n"
                    result["sources"].append(url)
                    logger.info(f"✅ Extracted {len(page_text)} characters from {page_type}")

            # Store the collected text for LLM extraction
            result["collected_text"] = all_text[:10000]  # Limit to 10k chars
            result["text_length"] = len(all_text)

            logger.info(f"✅ Scraping complete for {company_name}")

        except Exception as e:
            logger.error(f"❌ Error scraping {company_name}: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

