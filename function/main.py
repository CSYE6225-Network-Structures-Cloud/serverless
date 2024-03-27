import base64
import json
import requests
import os
import psycopg2
from datetime import datetime, timedelta
import functions_framework

domain_name = "snehilaryan32.store"
port = 8080
mail_api_key =  "296e917ecc3a1abe25b5835d3397c03f-f68a26c9-75ff923b"


db_host = os.getenv('DB_HOST')
print(f"DB_HOST: {db_host}")

db_port = os.getenv('DB_PORT')
print(f"DB_PORT: {db_port}")

db_name = os.getenv('DB_NAME')
print(f"DB_NAME: {db_name}")

db_user = os.getenv('DB_USER')
print(f"DB_USER: {db_user}")

db_password = os.getenv('DB_PASSWORD')
print(f"DB_PASSWORD: {db_password}")



def insert_into_email_tracker(verification_token, email):
        
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    cur = conn.cursor()
    sent_time = datetime.now() + timedelta(minutes=2)
    cur.execute(
        "INSERT INTO email_tracker (verification_token, email, expire_time) VALUES (%s, %s, %s)",
        (verification_token, email, sent_time)
    )
    conn.commit()

def generate_verification_link(token_uuid):
    # Generate the verification link
    link = f"http://{domain_name}:{port}/verify-email/{token_uuid}"
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
    insert_into_email_tracker(verification_token = link, email = email)