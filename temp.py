# import smtplib
#
# # creates SMTP session
# s = smtplib.SMTP('smtp.gmail.com', 587)
#
# # start TLS for security
# s.starttls()
#
# # Authentication
# s.login("aadeshkabra@gmail.com", "inximuqzuxdotmks")
#
# # message to be sent
# message = "Hi, you have password reset111 request."
#
# # sending the mail
# s.sendmail("aadeshkabra@gmail.com", "aadesh.kabra20@vit.edu", message)
#
# # terminating the session
# s.quit()


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "aadeshkabra@gmail.com"
receiver_email = "aadesh.kabra20@vit.edu"
password = "inximuqzuxdotmks"
subject = "Subject of the email"
message = "Body of the email"

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(message, 'plain'))

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(sender_email, password)
text = msg.as_string()
server.sendmail(sender_email, receiver_email, text)
server.quit()
