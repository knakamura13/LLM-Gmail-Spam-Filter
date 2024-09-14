import base64

from bs4 import BeautifulSoup
from decouple import config
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI

from .models import LogEntry

# Define Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Load OpenAI API key from environment variables
client = OpenAI(api_key=config('OPENAI_API_KEY'))


# Logging function to store log messages in the database
def log_message(message):
    LogEntry.objects.create(message=message)


# Function to fetch latest emails from Gmail
def fetch_latest_emails(service):
    """Fetch the 5 latest emails using the Gmail API."""
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    return results.get('messages', [])


# Function to retrieve the email body from the message
def get_email_body(message):
    """Extract the body of the email and strip HTML content."""
    payload = message.get('payload', {})
    body_data = None

    if 'body' in payload and 'data' in payload['body']:
        body_data = payload['body']['data']
    elif 'parts' in payload:
        for part in payload['parts']:
            if 'body' in part and 'data' in part['body']:
                body_data = part['body']['data']
                break

    if body_data:
        decoded_body = base64.urlsafe_b64decode(body_data.encode('UTF-8')).decode('UTF-8')

        # Strip HTML tags and return plain text
        soup = BeautifulSoup(decoded_body, 'html.parser')
        return soup.get_text(separator="\n").strip()

    return ''


# Function to add a spam label to the email
# def add_spam_label(service, message_id):
#     """Apply the SPAM label to the email."""
#     labels = {'removeLabelIds': [], 'addLabelIds': ['SPAM']}
#     service.users().messages().modify(userId='me', id=message_id, body=labels).execute()


# Function to classify the email using OpenAI GPT
def classify_email(email_body: str, email_sender: str = '', email_subject: str = ''):
    """Classify email content as spam or not using OpenAI GPT, with error handling for rate limits."""
    try:
        # Pre-classification logic: if the sender is from a known marketing or blacklisted domain, skip classification
        marketing_domains = ['@bankofamerica.com']
        if any(domain in email_sender for domain in marketing_domains):
            log_message(f"Skipped classification for known marketing domain: {email_sender}")
            return False  # Consider known marketing emails as "not spam"

        blacklist_domains = ['@contact.kamalaharris.com']
        if any(domain in email_sender for domain in blacklist_domains):
            log_message(f"Skipped classification for known blacklisted domain: {email_sender}")
            return True  # Consider known blacklisted senders as "spam"

        # Pre-classificaiton logic: if the body is empty or the body/subject contains specific blacklisted phrases, skip classification
        blacklist_phrases = ['free gift', 'free offer', 'promotional offer', 'donate', 'donating', 'donation', 'Obama', 'Kamala',
                             'Walz', 'Trump']
        if (not len(email_body)
                or any(keyword in email_body.lower() for keyword in blacklist_phrases)
                or any(domain in email_subject for domain in blacklist_phrases)):
            log_message(f"Skipped classification for empty or specific keyword email: {email_sender}")
            return True  # Consider empty or specific keyword emails as "spam"

        # Format the prompt for GPT API
        sender_name = email_sender.split('@')[0] if email_sender else 'Unknown'
        prompt = f"""
You are tasked with reviewing the following email to determine if it is spam or not. 
Respond with either "spam" or "not spam".
EMAIL SENDER NAME AND ADDRESS: "{sender_name}"
EMAIL BODY (delimited by triple-backticks): ```{email_body}```
"""

        # Call the GPT API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an email classification assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the classification
        classification = response['choices'][0]['message']['content']

        # Log the full response and classification for debugging
        log_message(f"GPT API Response: {response}")
        log_message(f"Classification result: {classification}")

        # Return True if classified as spam
        return "spam" in classification.lower()

    except Exception as e:
        # Log any errors, including rate limits or other issues
        log_message(f"Error during classification: {str(e)}")
        return None  # Return None if an error occurs


# Function to fetch and classify the latest emails
def fetch_and_classify_latest_emails():
    """Fetch and classify the latest 5 emails, then modify their labels."""
    creds = Credentials.from_authorized_user_file(config('GOOGLE_API_TOKEN_PATH'), SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # Fetch the 5 latest emails
    messages = fetch_latest_emails(service)

    classified_emails = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers = msg.get('payload', {}).get('headers', [])

        # Extract subject, sender, and email body
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        body = get_email_body(msg)
        body_sample = body[:500].strip()  # Get the first 500 characters, stripped of leading/trailing whitespace

        # Classify the email as spam or not spam
        is_spam = classify_email(body_sample, sender, subject)

        # Apply label to the email and store the result
        classification = 'spam' if is_spam else 'not spam'

        classified_emails.append({
            'subject': subject,
            'sender': sender,
            'body': body_sample,
            'classification': classification
        })

    return classified_emails
