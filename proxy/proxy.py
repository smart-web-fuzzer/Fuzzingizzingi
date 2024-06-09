import sys
import signal
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proxy.logger import Logger
from proxy.traffic_interceptor import TrafficIntercept
from db_connector import create_connection

def signal_handler(server):
    def handler(signal, frame):
        print('Signal received, stopping server.')
        server.stop_server()
        sys.exit(0)
    return handler

if __name__ == "__main__":
    from proxy.network_listener import NetworkListener
    
    logger = Logger()
    logger.log("Starting the server...")

    port = 8888

    # 데이터베이스 연결 설정
    db_connection = create_connection(
        host_name="13.209.63.65",
        user_name="zzingzzingi",
        user_password="!Ru7eP@ssw0rD!12",
        db_name="fuzzingzzingi"
    )

    if db_connection.is_connected():
        logger.log("MySQL Fuzzingzzingi Database connection successful")

    interceptor = TrafficIntercept(db_connection=db_connection, logger=logger)
    server = NetworkListener(port=port, logger=logger, db_connection=db_connection, request_handler=interceptor.handle_client)
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(server)(s, f))
    
    try:
        server.start_server()
    except Exception as e:
        logger.log("Server encountered an error and stopped.")
        logger.log(str(e))