from django.http import JsonResponse

from .tasks import fetch_and_classify_latest_emails


def classify_emails_view(request):
    """Synchronously classify emails and return JSON data."""
    # Call the function directly (synchronously)
    classified_emails = fetch_and_classify_latest_emails()

    # Return the classification result
    return JsonResponse({'classified_emails': classified_emails})
