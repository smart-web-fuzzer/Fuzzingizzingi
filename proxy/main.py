import argparse
import logging
from server import CustomThreadingHTTPServer
from proxy_handler import CustomProxyRequestHandler
from cert_manager import generate_certs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-b", "--bind", default="0.0.0.0", help="Host to bind")  # 기본값을 0.0.0.0으로 설정
    parser.add_argument("-p", "--port", type=int, default=7777, help="Port to bind")
    parser.add_argument("-d", "--domain", default="*", help="Domain to intercept, if not set, intercept all.")
    parser.add_argument("--ca-key", default="ca-key.pem", help="CA key file")
    parser.add_argument("--ca-cert", default="ca-cert.pem", help="CA cert file")
    parser.add_argument("--cert-key", default="cert-key.pem", help="site cert key file")
    parser.add_argument("--cert-dir", default="certs", help="Site certs files")
    parser.add_argument("--make-certs", action='store_true', help="Generate certificates and exit")
    args = parser.parse_args()

    if args.make_certs:
        generate_certs(args.cert_dir)
        exit(0)

    protocol = "HTTP/1.1"

    class CustomHTTPServer(CustomThreadingHTTPServer):
        def __init__(self, server_address, RequestHandlerClass):
            super().__init__(server_address, RequestHandlerClass)
            self.args = args

    def handler(*handler_args, **handler_kwargs):
        CustomProxyRequestHandler(*handler_args, server_args=args, **handler_kwargs)

    httpd = CustomHTTPServer((args.bind, args.port), handler)
    logging.info(f"Serving HTTP on {args.bind} port {args.port} (http://{args.bind}:{args.port}/) ...")
    httpd.serve_forever()