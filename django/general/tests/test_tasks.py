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
        mock_response.text = "a,b,c\n1,2,3\n"
        mock_post.return_value = mock_response
        test_input = {"a": 1, "b": 2, "c": 3}
        task_result = calculate_mse(test_input)
        mock_post.assert_called_once_with(
            self.test_url,
            data=json.dumps(test_input),
            headers={"Content-type": "application/json"},
            timeout=200
        )
        self.assertEqual(task_result, "a,b,c\n1,2,3\n")

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
