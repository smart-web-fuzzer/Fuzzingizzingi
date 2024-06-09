import subprocess

def create_certificate(domain):
    # Let's Encrypt Certbot 사용
    subprocess.run([
        "sudo", "certbot", "certonly", "--standalone", 
        "--non-interactive", "--agree-tos", 
        "-d", domain, "--email", "numbbvi@naver.com"
    ])

    key_file = f"/etc/letsencrypt/live/{domain}/privkey.pem"
    crt_file = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
    ca_file = crt_file

    return key_file, crt_file, ca_file

def update_nginx_config(domain, key_file, crt_file, ca_file):
    server_ip = "13.209.63.65"
    server_port = 8888

    nginx_config = f"""
    server {{
        listen 80;
        server_name {domain};
        return 301 https://$server_name$request_uri;
    }}

    server {{
        listen 443 ssl;
        server_name {domain};

        ssl_certificate {crt_file};
        ssl_certificate_key {key_file};
        ssl_trusted_certificate {ca_file};

        location / {{
            proxy_pass http://{server_ip}:{server_port};
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }}
    }}
    """

    config_path = f"/etc/nginx/sites-available/{domain}"
    with open(config_path, "w") as file:
        file.write(nginx_config)

    subprocess.run(["sudo", "ln", "-sf", config_path, f"/etc/nginx/sites-enabled/{domain}"])
    subprocess.run(["sudo", "systemctl", "restart", "nginx"])
