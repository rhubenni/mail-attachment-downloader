# #################################################################################################### #
# # Mail Attachment Downloader ####################################################################### #
# # Version: 1.0.0             ####################################################################### #
# # Author: Rubeni Andrade     ####################################################################### #
# #################################################################################################### #
# # IMAP Handler                                                                                     # #
# #################################################################################################### #
# # Changelog:                                                                                       # #
# # 2020-08-29   - 1.0.0         - Initial Release                                                   # #
# #################################################################################################### #

import re
import os
from sqlhandler import SQLHandler
import pyodbc, pyodbc_config

DEBUG_MODE = True

def MonitorLog(RuleId, MailId, ExecutionStatus, ExecutionMessage, debugLevel = False):
    if DEBUG_MODE == False and debugLevel == True:
            return
    else:
        try:
            sqlstmt = """
                        INSERT INTO """ + pyodbc_config.SQLSRV_TABLES['monitor_log'] + """
                        ([RuleId],[MailId],[ExecutionStatus],[ExecutionMessage])
                        VALUES (?,?,?,?)
            """
            sqlh = SQLHandler()
            cursor = sqlh.conn.cursor()
            cursor.execute(sqlstmt, RuleId, MailId, ExecutionStatus, ExecutionMessage)
            cursor.commit()
            if DEBUG_MODE == True:
                print(RuleId, MailId, ExecutionStatus, ExecutionMessage)

        except pyodbc.Error as ex:
            print('An error occurred while writing the log to the database')


class MailMonitorHandler:
    ROOT_SAVEPATH = None

    def __init__(self):
        self.sqlh = SQLHandler()
        self.conn = self.sqlh.conn
        self.mails_matched_ok = []
        self.mails_matched_failure = []
        self.mails_not_matched = []

    def get_monitor_list(self):
        sql_list = """
            SELECT		 [RuleId]
                        ,[Sender]
                        ,[SubjectText]
                        ,[SubjectSearchMode]
                        ,[ContentType]
                        ,[AttachmentName]
                        ,[AttachmentSearchMode]
                        ,[SavePath]
            FROM		""" + pyodbc_config.SQLSRV_TABLES['monitor_list'] + """
            WHERE		[Enabled] = 1
        """

        try:
            self.rules = self.sqlh.fetch_query(sql_list)
        except:
            MonitorLog('-1', '-1', 'FATAL', 'An error occurred while fetching email rules from the database server')
            raise SystemError


    def check_rule(self, searchmode, searchtext, mailtext):
        if searchmode == 'StartsWith' and mailtext.startswith(searchtext):
            return True
        elif searchmode == 'EndsWith' and mailtext.endswith(searchtext):
            return True
        elif searchmode == 'Contains' and searchtext in mailtext:
            return True
        elif searchmode == 'Equals' and searchtext == mailtext:
            return True
        elif searchmode == 'Regex':
            return bool(re.match(searchtext,mailtext))
        else:
            return False


    def ensuredir(self, path):
        if os.path.isdir(path) == False:
            os.makedirs(path, exist_ok=True)


    def check_messages(self, messages):
        for rule in self.rules:
            for msg in messages:
                if self.check_rule('EndsWith', '<' + rule['Sender'] + '>', msg['sender']):
                    MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'VALIDATION', "Mail #" + str(msg['mail_id']) + ' - Passed sender rule - ' + str(msg['sender']), True)
                    if self.check_rule(rule['SubjectSearchMode'], rule['SubjectText'], msg['subject']):
                        MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'VALIDATION', "Mail #" + str(msg['mail_id']) + ' - Passed subject rule - ' + str(msg['subject']), True)
                        for attach in msg['attach']:
                            if rule['AttachmentName'] == '$any' or self.check_rule(rule['AttachmentSearchMode'], rule['AttachmentName'], attach['filename']):
                                MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'VALIDATION', "Matched Rule #" + str(rule['RuleId']) + ' - match attachment name rule - ' + rule['AttachmentName'] + ': Saving file ' + str(attach['filename']) + ' on ' + rule['SavePath'] + '...')

                                rule['SavePath'] = rule['SavePath'].replace('\\', '/')

                                if rule['SavePath'].startswith('/'):
                                    rule['SavePath'] = rule['SavePath'][1:]

                                if not rule['SavePath'].endswith('/'):
                                    rule['SavePath'] = rule['SavePath'] + '/'

                                filepath = self.ROOT_SAVEPATH + rule['SavePath']
                                filenamepath = filepath + attach['filename']

                                try:
                                    self.ensuredir(filepath)
                                    open(filenamepath, "wb").write(attach['payload'].get_payload(decode=True))
                                    self.mails_matched_ok.append(msg['mail_id'])
                                    MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'SUCESS', "Rule #" + str(rule['RuleId']) + ': the ' + str(attach['filename']) + ' file was successfully saved to ' + rule['SavePath'] + '!')

                                except:
                                    self.mails_matched_failure.append(msg['mail_id'])
                                    MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'ERROR', "Rule #" + str(rule['RuleId']) + ': an error occurred while saving the file "' + filenamepath + '", it will be ignored.')
                            else:
                                MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'FAIL', "Rule #" + str(rule['RuleId']) + ': The e-mail rule was matched, but attachment "' + str(attach['filename']) + '" don\'t matches this rule')
                                self.mails_not_matched.append(msg['mail_id'])

                    else:
                        MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'FAIL', "Rule #" + str( rule['RuleId']) + ': The e-mail subject rule was not matched "' + str(msg['subject']) + '" expected value: ' + rule['SubjectText'], True)
                        self.mails_not_matched.append(msg['mail_id'])

                else:
                    MonitorLog(str(rule['RuleId']), str(msg['mail_id']), 'FAIL', "Rule #" + str( rule['RuleId']) + ': The e-mail sender rule was not matched "' + str(msg['sender']) + '" expected value: ' + rule['Sender'], True)
                    self.mails_not_matched.append(msg['mail_id'])
