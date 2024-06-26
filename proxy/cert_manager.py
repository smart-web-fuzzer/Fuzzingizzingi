import os
import subprocess

def generate_certs(cert_dir):
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    cert_key = os.path.join(cert_dir, 'cert-key.pem')
    cert_req = os.path.join(cert_dir, 'cert-req.pem')
    cert = os.path.join(cert_dir, 'ca-cert.pem')

    subprocess.run(['openssl', 'genrsa', '-out', cert_key, '2048'], check=True)
    subprocess.run(['openssl', 'req', '-new', '-key', cert_key, '-out', cert_req, '-subj', '/CN=example.com'], check=True)
    subprocess.run(['openssl', 'x509', '-req', '-days', '365', '-in', cert_req, '-signkey', cert_key, '-out', cert], check=True)
    
    os.remove(cert_req)  # 서명 요청 파일 삭제

    print(f"Certificates generated at {cert_dir}")
