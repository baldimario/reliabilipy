"""
Example of using reliabilipy for a resilient web scraper.
Shows retry with exponential backoff and circuit breaker patterns.
"""
import requests
from reliabilipy import retry, circuit_breaker

class ResilientWebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @retry(
        exceptions=(requests.RequestException,),
        backoff='exponential',
        max_retries=3,
        jitter=True
    )
    @circuit_breaker(
        failure_threshold=5,
        recovery_timeout=60,
        exceptions=(requests.RequestException,)
    )
    def fetch_page(self, path: str) -> str:
        """Fetch a page with automatic retries and circuit breaking."""
        url = f"{self.base_url}/{path}"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

def main():
    # Example usage
    scraper = ResilientWebScraper('https://api.example.com')
    
    try:
        # This will retry up to 3 times with exponential backoff if it fails
        content = scraper.fetch_page('data')
        print(f"Successfully fetched page: {len(content)} bytes")
    except requests.RequestException as e:
        print(f"Failed to fetch page after retries: {e}")
    except RuntimeError as e:
        print(f"Circuit breaker is open: {e}")

if __name__ == '__main__':
    main()
