import ssl
from certificate_manager import CertificateManager

class SSLManager:
    def __init__(self):
        self.cert_manager = CertificateManager()

    def create_ssl_context(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.cert_manager.get_cert_path(),
                                keyfile=self.cert_manager.get_key_path())
        return context

if __name__ == "__main__":
    ssl_manager = SSLManager()
    context = ssl_manager.create_ssl_context()