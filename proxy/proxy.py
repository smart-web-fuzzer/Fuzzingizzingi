import sys
import signal
from network_listener import NetworkListener
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

    # Start the network listener
    port = 8888
    server = NetworkListener(port=port, logger=logger)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        server.start_server()
    except Exception as e:
        logger.log("Server encountered an error and stopped.")
