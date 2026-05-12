import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)
server.set_debuglevel(1)

server.ehlo()
server.starttls()
server.ehlo()

server.login('ani.memory.project@gmail.com', 'fqqwfuvuxrftuyvv')

print("LOGIN OK")

server.quit()