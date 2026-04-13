from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import os
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FOLDER = os.path.join(BASE_DIR, "..", "..", r"app/utils/certs")
CERT_FOLDER = os.path.normpath(CERT_FOLDER)

def get_cert_and_key(folder_path=CERT_FOLDER):
    cert_pattern = re.compile(r"client-.*\.crt$")
    key_pattern = re.compile(r"client-.*\.key$")

    cert_file = None
    key_file = None

    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        if cert_pattern.match(file):
            cert_file = full_path

        elif key_pattern.match(file):
            key_file = full_path

    if not cert_file or not key_file:
        raise FileNotFoundError("Missing client-*.crt or client-*.key")

    return cert_file, key_file

def get_cn_from_cert(cert_path):
    with open(cert_path, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    return cn
