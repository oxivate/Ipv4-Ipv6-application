# extra imports for cache and warnings
import json
import time
from pathlib import Path
import warnings

import requests
import typer
from typing import Optional
import unittest
from unittest.mock import patch
from urllib3.exceptions import InsecureRequestWarning

# Suppress insecure HTTPS warnings
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

CACHE_FILE = Path.home() / ".cache" / "ipinfo_cache.json"
CACHE_TTL = 24 * 3600  # 24 hours

def load_cache(ip_address: str) -> dict | None:
    if not CACHE_FILE.exists():
        return None
    data = json.loads(CACHE_FILE.read_text())
    entry = data.get(ip_address)
    if not entry or (time.time() - entry["timestamp"] > CACHE_TTL):
        return None
    return entry["info"]

def save_cache(ip_address: str, info: dict):
    data: dict = {}
    if CACHE_FILE.exists():
        data = json.loads(CACHE_FILE.read_text())
    data[ip_address] = {"timestamp": time.time(), "info": info}
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data))

app = typer.Typer(
    help="CLI application to fetch public or target IP and geolocation info.",
    add_completion=False,
    no_args_is_help=True
)

def get_ip_address(
    ip_type: str = 'ipv4',
    proxy: Optional[str] = None
) -> str:
    if ip_type not in ('ipv4', 'ipv6'):
        typer.echo("Error: invalid IP type specified. Must be 'ipv4' or 'ipv6'.", err=True)
        raise typer.Exit(1)
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    urls = ["https://api.ipify.org"] if ip_type == 'ipv4' else [
        "https://api6.ipify.org",
        "https://ipv6.icanhazip.com"
    ]
    last_error = None
    for url in urls:
        try:
            resp = requests.get(url, proxies=proxies, verify=False, timeout=5)
            resp.raise_for_status()
            return resp.text.strip()
        except requests.RequestException as e:
            last_error = e
    if ip_type == 'ipv6':
        typer.echo(
            "Unable to retrieve an IPv6 address: your environment does not appear to support IPv6 or DNS resolution failed.",
            err=True
        )
    else:
        typer.echo(f"Error fetching IPv4 address: {last_error}", err=True)
    raise typer.Exit(1)

def get_ip_info(
    ip_address: str,
    proxy: Optional[str] = None,
    skip_cache: bool=False
) -> dict:
    if not skip_cache:
        cached = load_cache(ip_address)
        if cached:
            return cached
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        resp = requests.get(
            f"https://ipapi.co/{ip_address}/json/",
            proxies=proxies,
            verify=False,
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get('error'):
            typer.echo(f"API error: {data['error']}", err=True)
            raise typer.Exit(1)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            typer.echo("Rate limit reached on ipapi.co, using fallback...", err=True)
            try:
                fb = requests.get(
                    f"https://geolocation-db.com/json/{ip_address}&position=true",
                    proxies=proxies,
                    verify=False,
                    timeout=5
                )
                fb.raise_for_status()
                fbdata = fb.json()
                data = {
                    "country_name": fbdata.get("country_name") or fbdata.get("country") or "N/A",
                    "city": fbdata.get("city") or "N/A",
                    "latitude": fbdata.get("latitude") or 0,
                    "longitude": fbdata.get("longitude") or 0,
                    "org": fbdata.get("IPv4") or "N/A",
                    "asn": "N/A"
                }
            except requests.RequestException as e2:
                typer.echo(f"Fallback service error: {e2}", err=True)
                raise typer.Exit(1)
        else:
            typer.echo(f"Error fetching IP information: {e}", err=True)
            raise typer.Exit(1)
    except requests.RequestException as e:
        typer.echo(f"Network error fetching IP information: {e}", err=True)
        raise typer.Exit(1)
    save_cache(ip_address, data)
    return data

@app.command()
def main(
    ip_type: str = typer.Argument(
        'ipv4',
        help='IP version to query (ipv4 or ipv6)'
    ),
    target_ip: Optional[str] = typer.Option(
        None,
        '--target-ip', '-t',
        help='If set, query this IP instead of fetching your own'
    ),
    proxy: Optional[str] = typer.Option(
        None,
        '--proxy', '-p',
        help='Proxy URL to use for requests'
    ),
    no_cache: bool = typer.Option(False, '--no-cache', help='Skip local cache and force API call')
) -> None:
    """
    Displays a public IP address (your own by default) and its geolocation.

    Examples:

      # Get your own IPv4 address and info
      python main.py ipv4

      # Get your own IPv6 address and info (if available)
      python main.py ipv6

      # Query info for 8.8.8.8 instead of your own IP
      python main.py ipv4 --target-ip 8.8.8.8

      # Query info for IPv6 Google DNS
      python main.py ipv6 --target-ip 2001:4860:4860::8888

      # Use a proxy for the request
      python main.py ipv4 --proxy http://127.0.0.1:8080

      # Verify proxy usage locally
      python main.py ipv4 --target-ip 190.158.28.100 --proxy http://127.0.0.1:8899

      # Run the full test suite
      python -m unittest main -v
    """
    if proxy:
        typer.echo(f"Using proxy: {proxy}")
    if target_ip:
        ip = target_ip
        typer.echo(f"Using target IP: {ip}")
    else:
        typer.echo(f"Querying {ip_type.upper()} address…")
        ip = get_ip_address(ip_type, proxy)
        typer.echo(f"Your public {ip_type.upper()} address is: {ip}")
    info = get_ip_info(ip, proxy, skip_cache=no_cache)
    typer.echo("\nGeolocation and ISP information:")
    typer.echo(f"  Country  : {info.get('country_name','N/A')}")
    typer.echo(f"  City     : {info.get('city','N/A')}")
    typer.echo(f"  Latitude : {info.get('latitude','N/A')}")
    typer.echo(f"  Longitude: {info.get('longitude','N/A')}")
    typer.echo(f"  ISP      : {info.get('org','N/A')}")
    typer.echo(f"  ASN      : {info.get('asn','N/A')}")

if __name__ == '__main__':
    app()

# ------------------------
# Unit tests
# ------------------------
class TestIpAddressApp(unittest.TestCase):

    @patch('main.load_cache', return_value=None)
    @patch('requests.get')
    def test_get_ip_info_success(self, mock_get, mock_cache):
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            "country_name": "US", "city": "NY", "latitude": 0,
            "longitude": 0, "org": "Org", "asn": "AS"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        info = get_ip_info("0.0.0.0")
        self.assertEqual(info["country_name"], "US")
        mock_get.assert_called_once_with(
            "https://ipapi.co/0.0.0.0/json/",
            proxies=None,
            verify=False,
            timeout=5
        )

    @patch('main.load_cache', return_value=None)
    @patch('requests.get')
    def test_get_ip_info_rate_limit_fallback(self, mock_get, mock_cache):
        response_429 = unittest.mock.Mock()
        response_429.status_code = 429
        http_err = requests.HTTPError(response=response_429)
        def side_effect(url, **kwargs):
            if 'ipapi.co' in url:
                raise http_err
            mock_fb = unittest.mock.Mock()
            mock_fb.json.return_value = {"country_name":"FB","city":"FBCITY","latitude":1,"longitude":2,"IPv4":"FBORG"}
            mock_fb.status_code = 200
            return mock_fb
        mock_get.side_effect = side_effect
        info = get_ip_info("1.2.3.4")
        self.assertEqual(info["country_name"], "FB")
        self.assertEqual(mock_get.call_count, 2)

    @patch('main.load_cache', return_value=None)
    @patch('requests.get')
    def test_get_ip_info_network_error(self, mock_get, mock_cache):
        mock_get.side_effect = requests.RequestException("fail")
        with self.assertRaises(typer.Exit):
            get_ip_info("1.2.3.4")

    @patch('requests.get')
    def test_get_ip_address_ipv4(self, mock_get):
        mock_resp = unittest.mock.Mock()
        mock_resp.text = "192.0.2.1"
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        ip_address = get_ip_address('ipv4')
        self.assertEqual(ip_address, "192.0.2.1")
        mock_get.assert_called_once_with(
            "https://api.ipify.org", proxies=None, verify=False, timeout=5
        )

    @patch('requests.get')
    def test_get_ip_address_ipv6(self, mock_get):
        mock_resp = unittest.mock.Mock()
        mock_resp.text = "2001:db8::1"
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        ip_address = get_ip_address('ipv6')
        self.assertEqual(ip_address, "2001:db8::1")
        mock_get.assert_called_once_with(
            "https://api6.ipify.org", proxies=None, verify=False, timeout=5
        )

    def test_get_ip_address_invalid_type(self):
        with self.assertRaises(typer.Exit):
            get_ip_address('invalid')

    @patch('main.load_cache', return_value=None)
    @patch('requests.get')
    def test_get_ip_address_request_error(self, mock_get, mock_cache):
        mock_get.side_effect = requests.RequestException("Request failed")
        with self.assertRaises(typer.Exit):
            get_ip_address('ipv4')
