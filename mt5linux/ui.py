import logging
import time


class UI:
    def __init__(self, conn):
        self.__conn = conn

    def search_server(self, server):
        if not server:
            logging.error("Server not provided")
            return
        self.__conn.execute(f'open("C:\\\\server", "w").write("{server}")')
        time.sleep(1)
