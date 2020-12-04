import os
import smtplib
import mimetypes

import config
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart

def send(to, subject, text, attachments=None, text_type='plain'):
    try:
        message = MIMEMultipart()
        message['From'] = config.MAIL_USER
        message['To'] = to
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(text, text_type, 'utf-8'))

        if attachments and len(attachments) > 0:
            for path in attachments:
                if not os.path.isfile(path):
                    continue
                ctype, encoding = mimetypes.guess_type(path)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                if maintype == 'text':
                    f = open(path)
                    attachment = MIMEText(f.read(), _subtype=subtype)
                    f.close()
                elif maintype == 'image':
                    f = open(path, 'rb')
                    attachment = MIMEImage(f.read(), _subtype=subtype)
                    f.close()
                elif maintype == 'audio':
                    f = open(path, 'rb')
                    attachment = MIMEAudio(f.read(), _subtype=subtype)
                    f.close()
                else:
                    f = open(path, 'rb')
                    attachment = MIMEBase(maintype, subtype)
                    attachment.set_payload(f.read())
                    f.close()
                    encoders.encode_base64(attachment)

                filename = os.path.basename(path)
                attachment.add_header('Content-Disposition', 'attachment', filename=filename.decode('utf-8').encode('gb2312'))
                message.attach(attachment)

        composed = message.as_string()
        server = smtplib.SMTP_SSL(config.MAIL_HOST)
        server.login(config.MAIL_USER, config.MAIL_PWD)
        server.sendmail(config.MAIL_USER, to, composed)
        server.quit()
    except Exception as ex:
        print('send err', ex) #TODO save in file