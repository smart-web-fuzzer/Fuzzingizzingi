import sys
import signal
from network_listener import NetworkListener
from certificate_manager import CertificateManager
from ssl_manager import SSLManager
from traffic_interceptor import TrafficIntercept
from request_modifier import HTTPRequest
from logger import Logger
# from performance import

def signal_handler(signal, frame):
    print('Signal received, stopping server.')
    server.stop_server()
    sys.exit(0)

if __name__ == "__main__":
    # Initialize logger
    logger = Logger()
    logger.log("Starting the server...")

    # Generate certificates
    cert_manager = CertificateManager(cert_path="wildcard_cert.pem", key_path="wildcard_key.pem")
    cert_manager.generate_private_key()
    cert_manager.generate_wildcard_cert(base_domain="example.com")

    # Setup SSL
    ssl_manager = SSLManager()
    context = ssl_manager.create_ssl_context()

    # Start the network listener
    port = 8888
    server = NetworkListener(port=port, ssl_context=context, logger=logger)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        server.start_server()
    except Exception as e:
        logger.log("Server encountered an error and stopped.")
