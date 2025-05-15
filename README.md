 # Ipv4-Ipv6-application cli

A command-line utility to fetch public IP addresses (IPv4/IPv6) and retrieve geolocation and ISP information, with advanced features like local caching, rate-limit fallback, and proxy support.

## Features

* **Automatic detection** of your public IPv4 or IPv6 address.
* **Target IP option** (`--target-ip`) to query any external IP.
* **Proxy support** with the `--proxy` option for HTTP(S) requests.
* **Local cache** (24-hour TTL) to minimize repeated API calls and avoid rate limits (HTTP 429).
* **Rate-limit fallback** to an alternate service when the primary API returns 429.
* **Suppress insecure HTTPS warnings** when disabling SSL verification.
* **Unit test suite** using `unittest` and mocks to ensure code reliability.

## Requirements

* Python 3.11 or later
* `pip` for installing dependencies

## Installation

```bash
# Clone this repository
git clone https://github.com/your_username/ipv4-ipv6-cli.git
cd ipv4-ipv6-cli

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Show help message
env/bin/python main.py --help

# Get your own public IPv4 address
env/bin/python main.py ipv4

# Get your own public IPv6 address (if available)
env/bin/python main.py ipv6

# Query geolocation for a specific IPv4 address
env/bin/python main.py ipv4 --target-ip 8.8.8.8

# Query geolocation for a specific IPv6 address
env/bin/python main.py ipv6 --target-ip 2001:4860:4860::8888

# Use an HTTP proxy for all requests
env/bin/python main.py ipv4 --proxy http://127.0.0.1:8899

# Force no-cache mode (skip local cache)
env/bin/python main.py ipv4 --no-cache
```

## Advanced Examples

```bash
# Verify proxy usage with detailed logs
proxy --log-level debug &
env/bin/python main.py ipv4 --target-ip 190.158.28.100 --proxy http://127.0.0.1:8899 --no-cache
```

## Running Tests

Discover and run all unit tests:

```bash
python -m unittest discover -v
```

Or with `pytest`:

```bash
pytest --maxfail=1 --disable-warnings -v
```

## Continuous Integration / Deployment

Two GitHub Actions workflows are provided in `.github/workflows/`:

* **run-tests.yml**: runs the unit tests on each push or pull request to `main`.
* **publish-release.yml**: builds distribution packages and uploads them as release assets when a Git tag `v*.*.*` is pushed.

## Project Structure

```
ipv4-ipv6-cli/
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── .github/
    └── workflows/
        ├── run-tests.yml
        └── publish-release.yml
```


## License

This project is licensed under the MIT License. See [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE) for details.
