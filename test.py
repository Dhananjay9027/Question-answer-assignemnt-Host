# import smtplib
# from email.message import EmailMessage

# EMAIL_ADDRESS = "dhananjaysaini055@gmail.com"
# EMAIL_PASSWORD = ""  # Your 16-char App Password

# msg = EmailMessage()
# msg["Subject"] = "Test Email"
# msg["From"] = EMAIL_ADDRESS
# msg["To"] = "jaithegreat22@gmail.com"
# msg.set_content("✅ If you see this, Gmail SMTP is working!")

# try:
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#         smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#         smtp.send_message(msg)
#         print("✅ Email sent successfully.")
# except Exception as e:
#     print(f"❌ Failed: {e}")
