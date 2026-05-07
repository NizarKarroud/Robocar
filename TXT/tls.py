import os
import re
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
import ssl

# Absolute path to THIS file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# certs folder in same directory
CERT_FOLDER = os.path.join(BASE_DIR, "certs")


def get_cert_and_key(folder_path=CERT_FOLDER):
    cert_pattern = re.compile(r"txt-.*\.crt$")
    key_pattern = re.compile(r"txt-.*\.key$")

    cert_file = None
    key_file = None

    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        if cert_pattern.match(file):
            cert_file = full_path

        elif key_pattern.match(file):
            key_file = full_path
        else :
            ca_file = full_path
            
    if not cert_file or not key_file or ca_file:
        raise FileNotFoundError(
            "Missing client-*.crt or client-*.key in {}".format(folder_path)
        )
    return cert_file, key_file , ca_file


def get_cn_from_cert(cert_path):
    with open(cert_path, "rb") as f:
        cert = x509.load_pem_x509_certificate(
            f.read(),
            default_backend()
        )
    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    return cn


def create_ssl_context(cert_file , key_file , ca_file):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile=cert_file,
        keyfile=key_file
    )
    ssl_context.load_verify_locations(ca_file)
    return ssl_context

print("CERT_FOLDER:", CERT_FOLDER)
print("FILES:", os.listdir(CERT_FOLDER))