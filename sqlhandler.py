# #################################################################################################### #
# # Mail Attachment Downloader ####################################################################### #
# # Version: 1.0.0             ####################################################################### #
# # Author: Rubeni Andrade     ####################################################################### #
# #################################################################################################### #
# # SQL Handler                                                                                      # #
# #################################################################################################### #
# # Changelog:                                                                                       # #
# # 2020-08-31   - 1.0.0         - Initial Release                                                   # #
# #################################################################################################### #


import pyodbc, pyodbc_config
import time

class SQLHandler:
    def __init__(self):
        driver_names = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
        sql_connection_string = (
                'Driver={' + driver_names[0] + '};'
                'Server=' + pyodbc_config.SQLSRV_CONFIG['server'] + ';'
                'Database=' + pyodbc_config.SQLSRV_CONFIG['database'] + ';'
                'Trusted_Connection=no;'
                'UID=' + pyodbc_config.SQLSRV_CONFIG['user'] + ';'
                'PWD=' + pyodbc_config.SQLSRV_CONFIG['pass'] + ';'
                'Application Name=Mail Attachment Downloader/1.0.0 (' + pyodbc_config.SQLSRV_CONFIG['appName'] + ');'
        )

        try:
            self.conn = pyodbc.connect(sql_connection_string)

        except pyodbc.Error as ex:
            print('[ERROR] Fatal Error: SQL Server connection can\'t be done')
            print(ex)
            time.sleep(60)
            raise SystemError

    def fetch_query(self, sql_stmt):
        cursor = self.conn.cursor()
        cursor.execute(sql_stmt)
        columns = [column[0] for column in cursor.description]
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))

        return data

