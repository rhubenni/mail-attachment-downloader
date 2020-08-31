# #################################################################################################### #
# # Mail Attachment Downloader ####################################################################### #
# # Version: 1.0.0             ####################################################################### #
# # Author: Rubeni Andrade     ####################################################################### #
# #################################################################################################### #
# # Main Module                                                                                      # #
# #################################################################################################### #
# # Changelog:                                                                                       # #
# # 2020-08-29   - 1.0.0         - Initial Release                                                   # #
# #################################################################################################### #

import os, sys
import pyodbc
from imaphandler import IMAPHandler
from monitorhandler import MailMonitorHandler

use_proxy = False


def proxy_config():
    global use_proxy
    if use_proxy is True:
        import proxy_config

        if proxy_config.USE_PYSOCKS_EXTENDED is True:
            # Add PySocks Extended (https://github.com/rhubenni/PySocksExtended)
            sys.path.append(os.getcwd() + '/../PySocksExtended')

        import socks, socket
        socks.PROXY_HTTP_AUTH_USERNAME = proxy_config.PROXY['user']
        socks.PROXY_HTTP_AUTH_PASSWORD = proxy_config.PROXY['pass']
        socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_config.PROXY['server'], proxy_config.PROXY['port'], True)
        socket.socket = socks.socksocket


def get_monitor_list():
    print(0)

if __name__ == '__main__':
    proxy_config()
    imap = IMAPHandler()
    imap.connect()
    imap.get_message_list()
    monitor = MailMonitorHandler()




