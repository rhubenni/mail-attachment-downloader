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

import imap_config
import imaplib
import email


class IMAPHandler:

    def __init__(self):
        self.imap = None
        self.messages = []

    def connect(self):
        imap_server = imaplib.IMAP4_SSL(imap_config.IMAP_CONFIG['server'], imap_config.IMAP_CONFIG['port'])
        imap_server.login(imap_config.IMAP_CONFIG['user'], imap_config.IMAP_CONFIG['pass'])
        imap_server.select()
        self.conn = imap_server

    @staticmethod
    def check_attachment(mail):
        if mail.is_multipart():
            attachment = []
            for part in mail.walk():
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachment.append({
                            "filename": filename,
                            "ContentType": part.get_content_type(),
                            "payload": part  # .get_payload(decode=True)
                        })
            if len(attachment) == 0:
                return None
            else:
                return attachment

    def get_message_list(self):
        self.conn.select("INBOX")
        (status, mails) = self.conn.search(None, '(UNSEEN)')

        if status != 'OK':
            print("Ocorreu um erro ao buscar as mensagens")
            raise SystemError

        for mail_id in mails[0].split(b' '):
            status, mail_obj = self.conn.fetch(mail_id, '(BODY.PEEK[])')  # '(RFC822)')
            if status != 'OK':
                print("Ocorreu um erro ao obter a mensagem ID #" + mail_id.decode())

            for r in mail_obj:
                if isinstance(r, tuple):
                    mail = email.message_from_bytes(r[1])
                    self.messages.append({
                        "mail_id": mail_id,
                        "sender": mail.get("From"),
                        "subject": email.header.decode_header(mail['Subject'])[0][0],
                        "recipient": mail.get("To"),
                        "carboncopy": mail.get("Cc"),
                        "attach": self.check_attachment(mail)
                    })
