from celery import shared_task

import json
import requests
from django.conf import settings

@shared_task(track_started=True)
def calculate_mse(mse_input):
    mse_url = settings.MSE_CALCULATOR_URL
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.post(mse_url, data=json.dumps(mse_input), headers=headers, timeout=200)
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError('An error has occurred. The connection to the MSE calculator was refused, probably because the server is not available.')
    else:
        if response.status_code == 500:
            raise requests.exceptions.HTTPError('The MSE server generated an internal error.')
        status = response.status_code
        results = response.text
    return results
