import re
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase

from general.models import TempMseUpload
from general.views import MultipleSystemsEstimation


class TestMseSetupView(TestCase):
    """Test the MultipleSystemsEstimationSetup view.

    There are no test for get or invalid input because validation is all handled by core Django.
    """

    def _make_file(self):
        file = SimpleUploadedFile("test.csv", b"1,2,3\n4,5,6", content_type="text/plain")
        return file

    def test_get_mse_post_valid_1(self):
        """Test posting valid data to the form."""
        client = Client()
        post_data = {"total_lists_required": 3, "file_upload": ""}
        response = client.post("/multiplesystemsestimation/setup", post_data)
        self.assertTrue("mode" in client.session)
        self.assertEqual(client.session["mode"], "new")
        self.assertRedirects(response, reverse("general:mse_calc"))

    def test_get_mse_post_valid_2(self):
        """Test posting valid data to the form."""
        client = Client()
        post_data = {"total_lists_required": "", "file_upload": self._make_file()}
        response = client.post("/multiplesystemsestimation/setup", post_data)
        self.assertTrue("mode" in client.session)
        self.assertEqual(client.session["mode"], "upload")
        self.assertRedirects(response, reverse("general:mse_calc"))


class TestMultipleSystemsEstimationExamplesView(TestCase):
    """Test the examples view.

    There are no test for get or invalid input because validation is all handled by core Django.
    """

    def test_get_mse_post_valid(self):
        """Test posting valid data to the form."""
        client = Client()
        post_data = {"example": "silverman_1"}
        response = client.post("/multiplesystemsestimation/examples", post_data)
        self.assertTrue("mode" in client.session)
        self.assertEqual(client.session["mode"], "example")
        self.assertRedirects(response, reverse("general:mse_calc"))


class TestMseView(TestCase):
    """Test the MultipleSystemsEstimation view."""

    def test__calculate_initial_data_with_3_lists(self):
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
            ],
        )
        result = MultipleSystemsEstimation()._calculate_initial_data(3)
        self.assertEqual(result, expected)

    def test__calculate_initial_data_with_4_lists(self):
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
            ],
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

    def test_get_with_no_session_data(self):
        """Test that we are redirected to the start page if there is no appropriate session data available."""
        client = Client()
        response = client.get("/multiplesystemsestimation/calculator")
        self.assertRedirects(response, reverse("general:mse"))

    def test_get_with_incorrect_mode_session_data(self):
        """Test that we are shown the error page if there is no appropriate mode available."""
        client = Client()
        session = client.session
        session["mode"] = "wrong"
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        self.assertTemplateUsed(response, "general/mse_error.html")

    def test_get_mode_new_but_missing_data(self):
        """Test that an error page is shown if the 'new' mode is missing the other data required."""
        client = Client()
        session = client.session
        session["mode"] = "new"
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        self.assertTemplateUsed(response, "general/mse_error.html")

    def test_get_mode_new_with_correct_data(self):
        """Test that the data entry page is shown if all of the required data is available."""
        client = Client()
        session = client.session
        session["mode"] = "new"
        session["total_lists_required"] = 3
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        response_string = response.content.decode()
        self.assertTemplateUsed(response, "general/mse_calculator.html")
        self.assertTrue('<table class="input-table">' in response_string)
        self.assertEqual(response_string.count("<th"), 4)
        self.assertEqual(response_string.count("<tr"), 8)

    def test_get_mode_upload_but_missing_data(self):
        """Test that an error is shown if the 'upload' mode is missing the other data required."""
        client = Client()
        session = client.session
        session["mode"] = "upload"
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        self.assertTemplateUsed(response, "general/mse_error.html")

    def test_get_mode_upload_with_correct_data(self):
        """Test that the data entry page is shown and populated if all of the required upload data is available."""
        csv_string = b"0\n0\n1,0,20\n0,1,30\n1,1,14"
        test_file = SimpleUploadedFile("test.csv", csv_string, content_type="text/plain")
        upload = TempMseUpload.objects.create(file=test_file)
        client = Client()
        session = client.session
        session["mode"] = "upload"
        session["upload_id"] = upload.id
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        response_string = response.content.decode()
        self.assertTemplateUsed(response, "general/mse_calculator.html")
        self.assertTrue('<table class="input-table">' in response_string)
        self.assertEqual(response_string.count("<th"), 3)
        self.assertEqual(response_string.count("<tr"), 4)
        first_line_string = (
            '<input type="text" aria-label="Total entries on list 1" id="id_form-0-total_appearances" '
            'name="form-0-total_appearances" value="20"'
        )
        self.assertTrue(first_line_string in re.sub(r"\s+", " ", response_string).strip())

    def test_get_mode_example_but_missing_data(self):
        """Test that an error is shown if the 'example' mode is missing the other data required."""
        client = Client()
        session = client.session
        session["mode"] = "example"
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        self.assertTemplateUsed(response, "general/mse_error.html")

    def test_get_mode_example_with_correct_data(self):
        """Test that the data entry page is shown and populated if all of the required example data is available."""
        client = Client()
        session = client.session
        session["mode"] = "example"
        session["example"] = "silverman_4"
        session.save()
        response = client.get("/multiplesystemsestimation/calculator")
        response_string = response.content.decode()
        self.assertTemplateUsed(response, "general/mse_calculator.html")
        self.assertTrue('<table class="input-table">' in response_string)
        self.assertEqual(response_string.count("<th"), 5)
        self.assertEqual(response_string.count("<tr"), 16)
        first_line_string = (
            '<input type="text" aria-label="Total entries on list 1" id="id_form-0-total_appearances" '
            'name="form-0-total_appearances" value="1131"'
        )
        self.assertTrue(first_line_string in re.sub(r"\s+", " ", response_string).strip())

    @patch("general.views.calculate_mse.delay")
    def test_post_mse_valid(self, mock_task):
        """Test the post to the mse calculator with valid data."""
        client = Client()
        post_data = {
            "total_lists": "2",
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "3",
            "form-0-index_pos": "0",
            "form-0-required_lists": "list 1",
            "form-0-total_appearances": "34",
            "form-1-index_pos": "1",
            "form-1-required_lists": "list 2",
            "form-1-total_appearances": "32",
            "form-2-index_pos": "2",
            "form-2-required_lists": "list 1|list 2",
            "form-2-total_appearances": "20",
            "censoring_lower": "0",
            "censoring_upper": "0",
            "model_type": "NBE",
        }
        response = client.post("/multiplesystemsestimation/calculator", post_data)
        mock_task.assert_called_once()
        response_string = response.content.decode()
        self.assertTrue("<h2>Results</h2>" in response_string)
        download_string = 'input type="hidden" name="csv-data" value="0|||0|||1|0|34|||0|1|32|||1|1|20|||"'
        self.assertTrue(download_string in re.sub(r"\s+", " ", response_string).strip())

    def test_post_mse_invalid_data(self):
        """Test the post to the mse calculator with invalid data."""
        client = Client()
        post_data = {
            "total_lists": "2",
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-index_pos": "0",
            "form-0-required_lists": "list 1",
            "form-0-total_appearances": "invalid",
            "form-1-index_pos": "1",
            "form-1-required_lists": "list 2",
            "form-1-total_appearances": "32",
            "form-2-index_pos": "2",
            "form-2-required_lists": "list 1|list 2",
            "form-2-total_appearances": "",
            "censoring_lower": "0",
            "censoring_upper": "0",
            "model_type": "NBE",
        }
        response = client.post("/multiplesystemsestimation/calculator", post_data)
        response_string = response.content.decode()
        self.assertFalse('<table class="results-table">' in response_string)
        self.assertFalse("<h2>Results</h2>" in response_string)
        self.assertFalse('value="1|0|34|||0|1|32|||1|1|-|||"' in response_string)
        self.assertFalse('<input type="submit" value="Download input data and results"/>' in response_string)
        self.assertTrue("<li>Total must be an integer or * (* is used for censored data)" in response_string)
        self.assertTrue('<table class="input-table">' in response_string)
        self.assertEqual(response_string.count("<th"), 3)
        self.assertEqual(response_string.count("<tr"), 4)


class TestMultipleSystemsEstimationDownloadView(TestCase):
    pass


class TestPollState(TestCase):
    pass