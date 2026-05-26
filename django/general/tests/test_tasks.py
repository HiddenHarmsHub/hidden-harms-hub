import json
from unittest.mock import MagicMock, patch

import requests
from django.conf import settings
from django.test import TestCase

from general.tasks import calculate_mse


class TestMseTasks(TestCase):
    """Test the Tasks."""

    def setUp(self):
        """Add test url which will never be hit due to mocking."""
        self.test_url = "localhost:5000/calculate_mse"
        settings.MSE_CALCULATOR_URL = self.test_url

    @patch("general.tasks.requests.post")
    def test_calculate_mse_task_success(self, mock_post):
        """Test that request is called with the right data and returns the result."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_text = """
            parameter,estimate,ci_lower,ci_upper\n
            alpha,5.248895,3.395394,6.6492987\n
            beta_1,-1.9524562,-3.4493365,-0.68000245\n
            beta_2,-1.6629716,-3.2102783,-0.37538695\n
            beta_3,-2.355661,-3.8829818,-1.2214549\n
            gamma_12,0.45588067,-1.0248151,1.4809868\n
            gamma_13,0.9122592,-0.30105764,1.8032496\n
            gamma_23,1.4185445,0.21890734,2.6326616\n
        """
        mock_response.text = response_text
        mock_post.return_value = mock_response
        test_input = {
            "list_data": [30, 40, 20, 10, 7, 18, 9],
            "censoring_lower": 0,
            "censoring_upper": 0,
            "total_lists": 3,
            "model_type": "NBE",
        }
        task_result = calculate_mse(test_input)
        mock_post.assert_called_once_with(
            self.test_url, data=json.dumps(test_input), headers={"Content-type": "application/json"}, timeout=200
        )
        self.assertEqual(task_result[0], response_text)
        self.assertEqual(task_result[1], "NBE")

    @patch("general.tasks.requests.post")
    def test_calculate_mse_task_no_connection(self, mock_post):
        """Test that an appropriate error is returned if the server cannot be contacted."""
        mock_post.side_effect = requests.exceptions.ConnectionError("server not available")
        with self.assertRaises(requests.exceptions.ConnectionError) as run_context:
            calculate_mse({})
        self.assertIn("the connection to the mse calculator was refused", str(run_context.exception).lower())

    @patch("general.tasks.requests.post")
    def test_calculate_mse_task_500_error(self, mock_post):
        """Test that an appropriate error is returned if the server raise an error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        with self.assertRaises(requests.exceptions.HTTPError) as run_context:
            calculate_mse({})
        self.assertEqual("the mse server generated an internal error.", str(run_context.exception).lower())
