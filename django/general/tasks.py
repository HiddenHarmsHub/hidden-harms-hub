import json
from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django_celery_results.models import TaskResult


@shared_task(track_started=True)
def calculate_mse(mse_input):
    """Send the data to the MSE server to run the calculation.

    Args:
        mse_input (dict): The input data for the MSE calculation.

    Returns:
        str: The MSE results as a csv string.

    Raises:
        requests.exceptions.ConnectionError: Raised if the MSE server could not be contacted.
        requests.exceptions.HTTPError: Raised if the MSE server raised an internal error.
    """
    mse_url = settings.MSE_CALCULATOR_URL
    headers = {"Content-type": "application/json"}
    try:
        response = requests.post(mse_url, data=json.dumps(mse_input), headers=headers, timeout=200)
    except requests.exceptions.ConnectionError as connection_error:
        raise requests.exceptions.ConnectionError(
            "An error has occurred. The connection to the MSE calculator was refused, probably because "
            "the server is not available."
        ) from connection_error
    else:
        if response.status_code == 500:
            raise requests.exceptions.HTTPError("The MSE server generated an internal error.")
        results = response.text
    return results, mse_input['model_type']


@shared_task
def clean_database():
    """Remove any celery task results objects from the database if they are more than one hour old.

    Run as a scheduled task.
    """
    cut_off_time = timezone.now() - timedelta(minutes=5)
    TaskResult.objects.filter(date_done__lt=cut_off_time).delete()
