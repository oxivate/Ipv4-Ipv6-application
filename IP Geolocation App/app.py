from flask import Flask, render_template, request
from ip_utils import get_ip_address, get_ip_info
import ipaddress

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    ip_type = request.form.get('ip_type')
    custom_ip = request.form.get('custom_ip')

    ip_address = custom_ip.strip() if custom_ip else get_ip_address(ip_type)

    if custom_ip and not is_public_ip(custom_ip):
        return render_template('index.html', error="Private or invalid IPs are not allowed.")

    if "Error" in ip_address:
        return render_template('index.html', error=ip_address)

    ip_info = get_ip_info(ip_address)

    print(ip_info)
    
    if isinstance(ip_info, str) and "Error" in ip_info:
        return render_template('index.html', error=ip_info)

    return render_template('index.html', ip=ip_address, info=ip_info)

def is_public_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False

if __name__ == '__main__':
    app.run(debug=True)


