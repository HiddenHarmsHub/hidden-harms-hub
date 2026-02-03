from unittest.mock import MagicMock, patch

from django.test import Client, TestCase

from general.views import MultipleSystemsEstimation


class TestMseView(TestCase):
    """Test the MultipleSystemsEstimation view."""

    def test__calculate_initial_data_with_3(self):
        """Test the input table data creation process with 3 lists."""
        expected = (
            ["list 1", "list 2", "list 3"],
            [
                {"required_lists": ["list 1"], "first": False},
                {"required_lists": ["list 2"], "first": False},
                {"required_lists": ["list 3"], "first": False},
                {"required_lists": ["list 1", "list 2"], "first": True},
                {"required_lists": ["list 1", "list 3"], "first": False},
                {"required_lists": ["list 2", "list 3"], "first": False},
                {"required_lists": ["list 1", "list 2", "list 3"], "first": True},
            ]
        )
        result = MultipleSystemsEstimation()._calculate_initial_data(3)
        self.assertEqual(result, expected)

    def test__calculate_initial_data_with_4(self):
        """Test the input table data creation process with 4 lists."""
        expected = (
            ["list 1", "list 2", "list 3", "list 4"],
            [
                {"required_lists": ["list 1"], "first": False},
                {"required_lists": ["list 2"], "first": False},
                {"required_lists": ["list 3"], "first": False},
                {"required_lists": ["list 4"], "first": False},
                {"required_lists": ["list 1", "list 2"], "first": True},
                {"required_lists": ["list 1", "list 3"], "first": False},
                {"required_lists": ["list 1", "list 4"], "first": False},
                {"required_lists": ["list 2", "list 3"], "first": False},
                {"required_lists": ["list 2", "list 4"], "first": False},
                {"required_lists": ["list 3", "list 4"], "first": False},
                {"required_lists": ["list 1", "list 2", "list 3"], "first": True},
                {"required_lists": ["list 1", "list 2", "list 4"], "first": False},
                {"required_lists": ["list 1", "list 3", "list 4"], "first": False},
                {"required_lists": ["list 2", "list 3", "list 4"], "first": False},
                {"required_lists": ["list 1", "list 2", "list 3", "list 4"], "first": True},
            ]
        )
        result = MultipleSystemsEstimation()._calculate_initial_data(4)
        self.assertEqual(result, expected)

    def test__add_uploaded_totals_no_censoring_data(self):
        """Test the initial data creation for uploaded data (just adds totals)."""
        initial = [
            {"required_lists": ["list 1"], "first": False},
            {"required_lists": ["list 2"], "first": False},
            {"required_lists": ["list 3"], "first": False},
            {"required_lists": ["list 1", "list 2"], "first": True},
            {"required_lists": ["list 1", "list 3"], "first": False},
            {"required_lists": ["list 2", "list 3"], "first": False},
            {"required_lists": ["list 1", "list 2", "list 3"], "first": True},
        ]
        rows = ["1,0,0,23", "0,1,0,14", "0,0,1,67", "1,1,0,0", "1,0,1,5", "0,1,1,*", "1,1,1,"]
        lists = ["list 1", "list 2", "list 3"]
        expected = [
            {"required_lists": ["list 1"], "first": False, "total_appearances": "23"},
            {"required_lists": ["list 2"], "first": False, "total_appearances": "14"},
            {"required_lists": ["list 3"], "first": False, "total_appearances": "67"},
            {"required_lists": ["list 1", "list 2"], "first": True, "total_appearances": "0"},
            {"required_lists": ["list 1", "list 3"], "first": False, "total_appearances": "5"},
            {"required_lists": ["list 2", "list 3"], "first": False, "total_appearances": "*"},
            {"required_lists": ["list 1", "list 2", "list 3"], "first": True, "total_appearances": ""},
        ]
        results = MultipleSystemsEstimation()._add_uploaded_totals(initial, rows, lists)
        self.assertEqual(results[0], expected)
        self.assertEqual(results[1], {})

    def test__add_uploaded_totals_with_censoring_data(self):
        """Test the initial data creation for uploaded data (just adds totals)."""
        initial = [
            {"required_lists": ["list 1"], "first": False},
            {"required_lists": ["list 2"], "first": False},
            {"required_lists": ["list 3"], "first": False},
            {"required_lists": ["list 1", "list 2"], "first": True},
            {"required_lists": ["list 1", "list 3"], "first": False},
            {"required_lists": ["list 2", "list 3"], "first": False},
            {"required_lists": ["list 1", "list 2", "list 3"], "first": True},
        ]
        rows = ["1", "9", "1,0,0,23", "0,1,0,14", "0,0,1,67", "1,1,0,0", "1,0,1,5", "0,1,1,*", "1,1,1,"]
        lists = ["list 1", "list 2", "list 3"]
        expected = [
            {"required_lists": ["list 1"], "first": False, "total_appearances": "23"},
            {"required_lists": ["list 2"], "first": False, "total_appearances": "14"},
            {"required_lists": ["list 3"], "first": False, "total_appearances": "67"},
            {"required_lists": ["list 1", "list 2"], "first": True, "total_appearances": "0"},
            {"required_lists": ["list 1", "list 3"], "first": False, "total_appearances": "5"},
            {"required_lists": ["list 2", "list 3"], "first": False, "total_appearances": "*"},
            {"required_lists": ["list 1", "list 2", "list 3"], "first": True, "total_appearances": ""},
        ]
        results = MultipleSystemsEstimation()._add_uploaded_totals(initial, rows, lists)
        self.assertEqual(results[0], expected)
        self.assertEqual(results[1], {"censoring_lower": "1", "censoring_upper": "9"})

    def test_get_mse(self):
        """Test the get stage of the MSE workflow."""
        client = Client()
        response = client.get('/multiplesystemsestimation/calculator')
        response_string = response.content.decode()
        self.assertTrue('name="total_lists_required"' in response_string)
        self.assertTrue('name="file_upload"' in response_string)
        self.assertTrue('<input id="submit-button" type="submit" value="Submit">' in response_string)

    def test_post_mse_stage_1_valid(self):
        """Test stage 1 of the MSE workflow where the number of lists is provided in the data."""
        client = Client()
        response = client.post('/multiplesystemsestimation/calculator', {'total_lists_required': '3'})
        response_string = response.content.decode()
        self.assertTrue('<table class="input-table">' in response_string)
        self.assertEqual(response_string.count('<th'), 4)
        self.assertEqual(response_string.count('<tr'), 8)

    @patch('general.views.requests')
    def test_post_mse_stage_2_valid(self, mock_requests):
        """Test stage 2 of the MSE workflow."""
        mock_requests = MagicMock()
        mock_requests.status_code = 200
        mock_requests.get.return_value = 'These are the results'
        client = Client()
        post_data = {
            "total_lists": "2",
            "form-TOTAL_FORMS":	"3",
            "form-INITIAL_FORMS": "3",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-index_pos": "0",
            "form-0-required_lists": "list 1",
            "form-0-total_appearances": "34",
            "form-1-index_pos": "1",
            "form-1-required_lists": "list 2",
            "form-1-total_appearances":	"32",
            "form-2-index_pos": "2",
            "form-2-required_lists": "list 1|list 2",
            "form-2-total_appearances":	"20",
            "censoring_lower": "0",
            "censoring_upper": "0",
        }
        response = client.post('/multiplesystemsestimation/calculator', post_data)
        response_string = response.content.decode()
        self.assertTrue('<table class="results-table">' in response_string)
        self.assertTrue('<h2>Results</h2>' in response_string)
        self.assertTrue('value="0|||0|||1|0|34|||0|1|32|||1|1|20|||"' in response_string)
        self.assertTrue('<input type="submit" value="Download input data and results"/>' in response_string)

    def test_post_mse_stage_2_invalid(self):
        """Test stage 2 of the MSE workflow."""
        client = Client()
        post_data = {
            "total_lists": "2",
            "form-TOTAL_FORMS":	"3",
            "form-INITIAL_FORMS": "3",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-index_pos": "0",
            "form-0-required_lists": "list 1",
            "form-0-total_appearances": "invalid",
            "form-1-index_pos": "1",
            "form-1-required_lists": "list 2",
            "form-1-total_appearances":	"32",
            "form-2-index_pos": "2",
            "form-2-required_lists": "list 1|list 2",
            "form-2-total_appearances":	"",
            "censoring_lower": "0",
            "censoring_upper": "0",
        }
        response = client.post("/multiplesystemsestimation/calculator", post_data)
        response_string = response.content.decode()
        self.assertFalse('<table class="results-table">' in response_string)
        self.assertFalse('<h2>Results</h2>' in response_string)
        self.assertFalse('value="1|0|34|||0|1|32|||1|1|-|||"' in response_string)
        self.assertFalse('<input type="submit" value="Download input data and results"/>' in response_string)
        self.assertTrue("<li>Total must be an integer or * (* is used for censored data)" in response_string)
        self.assertTrue("<table " in response_string)
        self.assertEqual(response_string.count("<th"), 3)
        self.assertEqual(response_string.count("<tr"), 4)
