from celery import shared_task

import json
import requests
from django.conf import settings

@shared_task(track_started=True)
def calculate_mse(mse_input):
    mse_url = settings.MSE_CALCULATOR_URL
    headers = {'Content-type': 'application/json'}
    response = requests.post(mse_url, data=json.dumps(mse_input), headers=headers, timeout=10)
    results = response.text
    return results
