import requests
import unittest
from unittest.mock import patch


def get_ip_address(ip_type='ipv4'):

    try:
        if ip_type == 'ipv6':
            response = requests.get("https://api6.ipify.org")
        elif ip_type == 'ipv4':
            response = requests.get("https://api.ipify.org")
        else:
            return "Error: Invalid IP type specified.  Must be 'ipv4' or 'ipv6'."

        response.raise_for_status()
        ip_address = response.text.strip()
        return ip_address
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to retrieve IP address: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
def get_ip_info(ip_address):

    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        response.raise_for_status()
        ip_info = response.json()
        if ip_info.get("error"):
            return f"Error from ipapi.co: {ip_info['error']}"
        return ip_info
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to retrieve IP information: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def display_ip_info(ip_type):

    ip_address = get_ip_address(ip_type)
    if "Error:" in ip_address:
        print(ip_address)
        return

    print(f"Your public {ip_type.upper()} address is: {ip_address}")
    ip_info = get_ip_info(ip_address)

    if isinstance(ip_info, str) and "Error:" in ip_info:
        print(ip_info)
        return

    if ip_info:
        print("\nGeolocation and ISP Information:")
        print(f"  Country: {ip_info.get('country_name', 'N/A')}")
        print(f"  City: {ip_info.get('city', 'N/A')}")
        print(f"  Latitude: {ip_info.get('latitude', 'N/A')}")
        print(f"  Longitude: {ip_info.get('longitude', 'N/A')}")
        print(f"  ISP: {ip_info.get('org', 'N/A')}")
        print(f"  ASN: {ip_info.get('asn', 'N/A')}")
    else:
        print("Could not retrieve geolocation and ISP information.")
def main():

    print("Welcome to the IP Information Application!")
    display_ip_info('ipv4')
    print("\n")
    display_ip_info('ipv6')
if __name__ == "__main__":
    main()

class TestIpAddressApp(unittest.TestCase):

    @patch('requests.get')
    def test_get_ip_address_ipv4(self, mock_get):

        mock_response = unittest.mock.Mock()
        mock_response.text = "192.0.2.1"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        ip_address = get_ip_address('ipv4')
        self.assertEqual(ip_address, "192.0.2.1")
        mock_get.assert_called_once_with("https://api.ipify.org")

    @patch('requests.get')
    def test_get_ip_address_ipv6(self, mock_get):

        mock_response = unittest.mock.Mock()
        mock_response.text = "2001:db8::1"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        ip_address = get_ip_address('ipv6')
        self.assertEqual(ip_address, "2001:db8::1")
        mock_get.assert_called_once_with("https://api6.ipify.org")

    @patch('requests.get')
    def test_get_ip_address_invalid_type(self, mock_get):

        ip_address = get_ip_address('invalid')
        self.assertEqual(ip_address, "Error: Invalid IP type specified.  Must be 'ipv4' or 'ipv6'.")
        mock_get.assert_not_called()

    @patch('requests.get')
    def test_get_ip_address_request_error(self, mock_get):

        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        ip_address = get_ip_address('ipv4')
        self.assertTrue(ip_address.startswith("Error: Failed to retrieve IP address:"))

    @patch('requests.get')
    def test_get_ip_info_success(self, mock_get):

        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            "country_name": "United States",
            "city": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "org": "Google LLC",
            "asn": "AS15169"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        ip_info = get_ip_info("192.0.2.1")
        expected_info = {
            "country_name": "United States",
            "city": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "org": "Google LLC",
            "asn": "AS15169"
        }
        self.assertEqual(ip_info, expected_info)
        mock_get.assert_called_once_with("https://ipapi.co/192.0.2.1/json/")

    @patch('requests.get')
    def test_get_ip_info_api_error(self, mock_get):

        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {"error": "Invalid IP address"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        ip_info = get_ip_info("invalid_ip")
        self.assertEqual(ip_info, "Error from ipapi.co: Invalid IP address")

    @patch('requests.get')
    def test_get_ip_info_request_error(self, mock_get):

        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        ip_info = get_ip_info("192.0.2.1")
        self.assertTrue(ip_info.startswith("Error: Failed to retrieve IP information:"))

    @patch('requests.get')
    def test_get_ip_info_unexpected_error(self, mock_get):

        mock_get.side_effect = Exception("Unexpected error")
        ip_info = get_ip_info("192.0.2.1")
        self.assertTrue(ip_info.startswith("An unexpected error occurred:"))
if __name__ == '__main__':
    unittest.main()


