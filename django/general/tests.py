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

    def test__add_uploaded_totals(self):
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
        self.assertEqual(results, expected)

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

    def test_post_mse_stage_2_valid(self):
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
            "form-0-total_appearances": "34",
            "form-1-index_pos": "1",
            "form-1-required_lists": "list 2",
            "form-1-total_appearances":	"32",
            "form-2-index_pos": "2",
            "form-2-required_lists": "list 1|list 2",
            "form-2-total_appearances":	"",
        }
        response = client.post('/multiplesystemsestimation/calculator', post_data)
        response_string = response.content.decode()
        self.assertTrue('<table class="results-table">' in response_string)
        self.assertTrue('<h2>Results</h2>' in response_string)
        self.assertTrue('value="1|0|34|||0|1|32|||1|1|-|||"' in response_string)
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
        }
        response = client.post("/multiplesystemsestimation/calculator", post_data)
        response_string = response.content.decode()
        self.assertFalse('<table class="results-table">' in response_string)
        self.assertFalse('<h2>Results</h2>' in response_string)
        self.assertFalse('value="1|0|34|||0|1|32|||1|1|-|||"' in response_string)
        self.assertFalse('<input type="submit" value="Download input data and results"/>' in response_string)
        self.assertTrue("<li>Total must be an integer, * or left empty</li>" in response_string)
        self.assertTrue('<table class="input-table">' in response_string)
        self.assertEqual(response_string.count("<th"), 3)
        self.assertEqual(response_string.count("<tr"), 4)
