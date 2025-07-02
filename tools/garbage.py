from tools.decorators import tool
import os
import subprocess
import sys

@tool(name="garbage", description="trashy trash")
def garbage() -> str:
    """
    Scrapes the example.com website using BeautifulSoup and returns the page content.
    Dynamically installs beautifulsoup4 if not already installed.
    """
    try:
        from bs4 import BeautifulSoup
        import requests
    except ImportError:
        # Install dependencies if missing
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "requests"])
        from bs4 import BeautifulSoup
        import requests

    response = requests.get('https://example.com')
    soup = BeautifulSoup(response.text, 'html.parser')
    return str(soup)