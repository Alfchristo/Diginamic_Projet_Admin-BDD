import time
import requests


def fetch_with_retry(url, max_retries=5, delay=60):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}. Retrying in {delay} seconds. Error: {e}")
            time.sleep(delay)

    print(f"Failed to fetch {url} after {max_retries} attempts.")
    return None
