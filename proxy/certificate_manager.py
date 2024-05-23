from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.oid import NameOID
# 유효기간 모듈
from datetime import datetime, timedelta

# 클래스 초기화
class CertificateManager:
    def __init__(self, cert_path="wildcard_cert.pem", key_path="wildcard_key.pem"):
        self.cert_path = cert_path
        self.key_path = key_path
        self.key = None
        # 디렉토리가 존재하지 않으면 생성
	# 개인 키 생성
    def generate_private_key(self):
        self.key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        with open(self.key_path, "wb") as f:
            f.write(self.key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
	# 인증서 생성
    def generate_wildcard_cert(self, base_domain="example.com"):
        if self.key is None:
            self.generate_private_key()
        
        wildcard_domain = f"*.{base_domain}"
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"KR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Seoul"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Seoul"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Fuzzingzzingi"),
            x509.NameAttribute(NameOID.COMMON_NAME, wildcard_domain),
        ])
        
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(wildcard_domain)]), critical=False)
            .sign(self.key, hashes.SHA256())
        )
        
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def get_cert_path(self):
        return self.cert_path

    def get_key_path(self):
        return self.key_path

if __name__ == "__main__":
    cm = CertificateManager(cert_path="wildcard_cert.pem", key_path="wildcard_key.pem")
    cm.generate_private_key()
    cm.generate_wildcard_cert(base_domain="example.com")