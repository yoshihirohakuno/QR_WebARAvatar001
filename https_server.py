"""
Simple HTTPS server that serves the web directory using a self-signed certificate.
Run with: python https_server.py
For phone access, set CERT_HOSTS=localhost,192.168.x.x before running.
"""
import ssl
import http.server
import ipaddress
import os
import subprocess
import sys

PORT = 8443
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
CERT_DIR = os.path.join(BASE_DIR, '.certs')
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')
CERT_HOSTS = [
    host.strip()
    for host in os.environ.get('CERT_HOSTS', 'localhost').split(',')
    if host.strip()
]

def openssl_san_extension():
    entries = []
    for host in CERT_HOSTS:
        try:
            ipaddress.ip_address(host)
            entries.append(f'IP:{host}')
        except ValueError:
            entries.append(f'DNS:{host}')
    return 'subjectAltName=' + ','.join(entries)

def generate_cert():
    """Generate a self-signed cert using the bundled Python's ssl module if possible."""
    os.makedirs(CERT_DIR, exist_ok=True)
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        print("Generating self-signed certificate...")
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'webar-local')])
        san_names = []
        for host in CERT_HOSTS:
            try:
                san_names.append(x509.IPAddress(ipaddress.ip_address(host)))
            except ValueError:
                san_names.append(x509.DNSName(host))
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(san_names), critical=False
            )
            .sign(key, hashes.SHA256())
        )
        with open(CERT_FILE, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(KEY_FILE, 'wb') as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            ))
        print("Certificate generated!")
        return True
    except ImportError:
        print("cryptography library not found, trying openssl command...")
        result = subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', KEY_FILE, '-out', CERT_FILE,
            '-days', '365', '-nodes',
            '-subj', '/CN=webar-local',
            '-addext', openssl_san_extension()
        ], capture_output=True)
        if result.returncode == 0:
            print("Certificate generated via openssl!")
            return True
        else:
            print("ERROR: Could not generate certificate:", result.stderr.decode())
            return False

if not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
    if not generate_cert():
        sys.exit(1)

os.chdir(WEB_DIR)

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(CERT_FILE, KEY_FILE)

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

server = http.server.HTTPServer(('0.0.0.0', PORT), NoCacheHandler)
server.socket = ctx.wrap_socket(server.socket, server_side=True)

print(f"\n=========================================")
print(f"  HTTPS Server running!")
for host in CERT_HOSTS:
    print(f"  URL:   https://{host}:{PORT}")
print(f"=========================================")
print(f"  NOTE: On first access, browser will warn about self-signed cert.")
print(f"  On iPhone Safari: tap 'Show Details' -> 'visit this website' -> Continue")
print(f"  On Android Chrome: tap 'Advanced' -> 'Proceed to server IP (unsafe)'")
print(f"=========================================\n")

server.serve_forever()
