# LLM Gmail Spam Filter

This project is a web-based email spam classifier built with Django. It utilizes OpenAI's GPT API to classify emails as either "spam" or "not spam" based on the email's contents and metadata, such as the sender's address.


## Installation

### Prerequisites

- Python 3.10+
- OpenAI API Key
- Gmail API Access (enabled via GCP)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/knakamura13/LLM-Gmail-Spam-Filter
   cd LLM-Gmail-Spam-Filter
   ```

2. Create a Conda environment:

   ```bash
   conda env create -n "llm-spam-filter" -f environment.yml
   ```

3. Set up environment variables for the OpenAI API. Create a `.env` file in the root directory and add:

   ```bash
   OPENAI_API_KEY="<your_openai_api_key_here>"
   GOOGLE_API_TOKEN_PATH=token.json
   ```

4. Run database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the Django development server:

   ```bash
   python manage.py runserver
   ```

## Usage

Navigate to `http://localhost:8000/emails/classify/` to view the email classification page.

## Project Structure (relevant files only)

```plaintext
├── django_gpt_email_spam_filter/
│   ├── settings.py
│   └── urls.py
├── email_classifier/
│   ├── views.py
│   ├── tasks.py
│   └── urls.py
├── templates/
│   └── email_classifier/
│       └── email_classification.html
├── README.md
├── requirements.txt
├── manage.py
├── get_google_token.py
├── credentials.json  # Used by `get_google_token.py` to generate `token.json`
├── token.json
└── .env  # Create this file
```

## Dependencies

- **Django**: Web framework.
- **OpenAI API**: For email classification using GPT models.
- **Google Auth API**: For email retrieval and filtering.
