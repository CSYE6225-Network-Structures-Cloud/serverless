import base64
import json
import requests
import os
import psycopg2
from datetime import datetime, timedelta
import functions_framework

domain_name = os.getenv('DOMAIN_NAME')
port = os.getenv('WEBAPP_PORT')
mail_api_key =  os.getenv('MAIL_GUN_API_KEY')
print(mail_api_key)
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
protocol = os.getenv('PROTOCOL')
endpoint = os.getenv('ENDPOINT')


def insert_into_email_tracker(verification_token, email):
        
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    try:
        cur = conn.cursor()
        sent_time = datetime.now() + timedelta(minutes=2)
        cur.execute(
            "INSERT INTO email_tracker (verification_token, email, expire_time) VALUES (%s, %s, %s)",
            (verification_token, email, sent_time)
        )
        conn.commit()
    finally:
        conn.close()
        print("Connection Closed From Cloud Function")


def generate_verification_link(token_uuid):
    # Generate the verification link
    # link = f"https://{domain_name}:{port}/verify-email/{token_uuid}"
    print(protocol)
    link = f"{protocol}://{domain_name}/{endpoint}/{token_uuid}"
    return link

def send_simple_message(recipient_email, verification_link):
    return requests.post(
    f"https://api.mailgun.net/v3/{domain_name}/messages",
    auth=("api", f"{mail_api_key}"),
    data={"from": f"Excited User <mailgun@{domain_name}>",
        "to": [recipient_email],
        "subject": "Hello",
        "text": "Testing template!", 
        "template": "Account Verify",
		"h:X-Mailgun-Variables": f'{{"link": "{verification_link}"}}'}).content


@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    message_fetched = base64.b64decode(cloud_event.data["message"]["data"])
    message_fetched = message_fetched.decode("utf-8") 
    message_dict = json.loads(message_fetched)
    email = message_dict["username"]
    token_id = message_dict["token_id"]
    link = generate_verification_link(token_id)
    print(message_dict)
    print(type(message_dict))
    print(send_simple_message(recipient_email=email, verification_link=link))
    insert_into_email_tracker(verification_token = token_id, email = email)