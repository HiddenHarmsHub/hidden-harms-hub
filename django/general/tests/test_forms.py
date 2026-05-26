from django.forms import formset_factory
from django.test import TestCase

from general.forms import BaseMseFormSet, MseDetailsForm


class TestMseFormSet(TestCase):
    """Test the MSE form set."""
    MseFormSet = formset_factory(MseDetailsForm, formset=BaseMseFormSet, extra=0)

    def build_formset_data(self, appearances, required_lists):
        """Build the formset data structure from the provided data.

        Args:
            appearances (list): The list of total_appearance data from the individual forms.
            required_lists (int): The number of lists required (is never actually used in tests)

        Returns:
            dict: The data structure required for the formset.
        """
        data = {
            "form-TOTAL_FORMS": str(len(appearances)),
            "form-INITIAL_FORMS": "0",
        }

        for i, entry in enumerate(appearances):
            data[f"form-{i}-index_pos"] = i
            data[f"form-{i}-required_lists"] = required_lists
            data[f"form-{i}-total_appearances"] = entry

        return data

    def test_valid_no_censoring(self):
        """Test a non-censored version of the data."""
        data = self.build_formset_data(["40", "30", "20", "10", "18", "4", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=0,
            censoring_upper=0,
        )
        self.assertTrue(formset.is_valid())

    def test_valid_with_censoring(self):
        """Test the form with some censoring."""
        data = self.build_formset_data(["40", "30", "20", "*", "18", "4", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=1,
            censoring_upper=3,
        )
        self.assertTrue(formset.is_valid())

    def test_invalid_star_not_allowed_when_censoring_upper_zero(self):
        """Test * not allowed in data if we are not censoring."""
        data = self.build_formset_data(["40", "30", "*", "10", "18", "9", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=0,
            censoring_upper=0,
        )
        self.assertFalse(formset.is_valid())
        self.assertIn(
            "Censoring upper must be greater than 0 if * is used in the data.",
            formset.non_form_errors()
        )

    def test_invalid_requires_star_when_censoring_upper_is_over_0(self):
        """Test * is required when we are censoring."""
        data = self.build_formset_data(["40", "30", "20", "10", "18", "9", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=1,
            censoring_upper=3,
        )
        self.assertFalse(formset.is_valid())
        self.assertIn(
            "If censoring upper is greater than 0 then some entries need to be censored with *.",
            formset.non_form_errors()
        )

    def test_invalid_no_values_allowed_in_censored_range_mid(self):
        """Test values within censored range not allowed (central number)."""
        data = self.build_formset_data(["40", "30", "20", "10", "18", "2", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=1,
            censoring_upper=3,
        )
        self.assertFalse(formset.is_valid())
        self.assertIn(
            "No values can fall in the censored range if censoring upper is greater than 0.",
            formset.non_form_errors()
        )

    def test_invalid_no_values_allowed_in_censored_range_edge_1(self):
        """Test values within censored range not allowed (lowest bound)."""
        data = self.build_formset_data(["40", "30", "20", "10", "18", "1", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=1,
            censoring_upper=3,
        )
        self.assertFalse(formset.is_valid())
        self.assertIn(
            "No values can fall in the censored range if censoring upper is greater than 0.",
            formset.non_form_errors()
        )

    def test_invalid_no_values_allowed_in_censored_range_edge_2(self):
        """Test values within censored range not allowed (upper bound)."""
        data = self.build_formset_data(["40", "30", "20", "10", "18", "3", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=1,
            censoring_upper=3,
        )
        self.assertFalse(formset.is_valid())
        self.assertIn(
            "No values can fall in the censored range if censoring upper is greater than 0.",
            formset.non_form_errors()
        )

    def test_valid_lower_value_than_censoring_lower(self):
        """Test values below censoring bounds are allowed."""
        data = self.build_formset_data(["40", "30", "*", "10", "18", "0", "12"], 3)
        formset = self.MseFormSet(
            data=data,
            censoring_lower=1,
            censoring_upper=3,
        )
        self.assertTrue(formset.is_valid())


class TestMseForms(TestCase):
    """Test the MSE form."""

    def test_mse_details_form_clean_valid_1(self):

        form = MseDetailsForm(data={"index_pos": 0, "required_lists": 3, "total_appearances": 1})

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_mse_details_form_clean_valid_2(self):

        form = MseDetailsForm(data={"index_pos": 0, "required_lists": 3, "total_appearances": "*"})

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_mse_details_form_clean_invalid(self):

        form = MseDetailsForm(data={"index_pos": 0, "required_lists": 3, "total_appearances": "test"})

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn("Total must be an integer or *", form.errors['__all__'][0])
