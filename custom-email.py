#!/usr/bin/env python3
import sys
import smtplib
import base64
from email.mime.text import MIMEText

MAILTRAP_USER = "REDACTED_FOR_SECURITY"
MAILTRAP_PASS = "REDACTED_FOR_SECURITY"

a = sys.argv[1] if len(sys.argv) > 1 else "alert"

m = MIMEText("Wazuh Alert Triggered\nFile: " + a)
m["Subject"] = "Wazuh Security Alert"
m["From"] = "wazuh@localhost"
m["To"] = "test@test.com"

c = base64.b64encode(("\x00" + MAILTRAP_USER + "\x00" + MAILTRAP_PASS).encode()).decode()

s = smtplib.SMTP("sandbox.smtp.mailtrap.io", 587)
s.ehlo()
s.starttls()
s.ehlo()

r = s.docmd("AUTH", "PLAIN " + c)
if r[0] != 235:
    sys.stderr.write("AUTHFAIL " + str(r) + "\n")
    sys.exit(1)

s.sendmail("wazuh@localhost", ["test@test.com"], m.as_string())
s.quit()