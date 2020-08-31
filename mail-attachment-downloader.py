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

sys.path.append(os.getcwd())
from imaphandler import IMAPHandler
from monitorhandler import MailMonitorHandler, MonitorLog

ROOT_SAVEPATH = 'B://'

def proxy_config():
    import proxy_config
    try:
        if proxy_config.USE_PROXY is True:
            if proxy_config.USE_PYSOCKS_EXTENDED is True:
                # Add PySocks Extended (https://github.com/rhubenni/PySocksExtended)
                sys.path.insert(0, os.getcwd() + '/../PySocksExtended')

            import socks, socket
            socks.PROXY_HTTP_AUTH_USERNAME = proxy_config.PROXY['user']
            socks.PROXY_HTTP_AUTH_PASSWORD = proxy_config.PROXY['pass']

            socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_config.PROXY['server'], proxy_config.PROXY['port'], True)
            socket.socket = socks.socksocket
    except:
        print("An error occurred while connecting to the proxy server...")
        MonitorLog('-1','-1','FATAL','An error occurred while connecting to the proxy server')
        raise SystemError


if __name__ == '__main__':
    proxy_config()
    try:
        imap = IMAPHandler()
        imap.connect()
    except:
        MonitorLog('-1','-1','FATAL','An error occurred while connecting to the IMAP server')
        raise SystemError

    try:
        imap.get_message_list()
    except:
        MonitorLog('-1','-1','FATAL','There was an error fetching emails from the IMAP server')
        raise SystemError

    monitor = MailMonitorHandler()
    monitor.ROOT_SAVEPATH = ROOT_SAVEPATH
    monitor.get_monitor_list()
    monitor.check_messages(imap.messages)
    print(monitor.mails_matched_ok)
    print(monitor.mails_matched_failure)
    print(monitor.mails_not_matched)




