import sys
import signal
from network_listener import NetworkListener
# from traffic_interceptor import TrafficIntercept
# from request_modifier import HTTPRequest
# from performance import

def signal_handler(server):
    def handler(signal, frame):
        print('Signal received, stopping server.')
        # 서버 중지
        server.stop_server()
        sys.exit(0)
    return handler

if __name__ == "__main__":
    logger = Logger()
    logger.log("Starting the server...")

    port = 8888
    server = NetworkListener(port=port, logger=logger)
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, server))
    
    try:
        server.start_server()
    except Exception as e:
        logger.log("Server encountered an error and stopped.")
        logger.log(str(e))