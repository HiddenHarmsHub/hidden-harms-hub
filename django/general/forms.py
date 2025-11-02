from django import forms
from django.core.exceptions import ValidationError


class MseSetupForm(forms.Form):
    """Form to setup the MSE main form."""
    total_lists_required = forms.IntegerField()


class MseForm(forms.Form):
    """Parent form to collect shared MSE data."""
    total_lists = forms.IntegerField()


class MseDetailsForm(forms.Form):
    """Form to collect MSE data for a single list combination."""
    index_pos = forms.IntegerField()
    required_lists = forms.CharField()
    total_appearances = forms.CharField(required=False)

    def clean(self):
        """Custom validation for the individual forms.

        Raises:
            ValidationError: raised if te data is not valid.
        """
        total = self.cleaned_data.get("total_appearances")
        if total != "*" and total != '':
            try:
                int(total)
            except ValueError:
                raise ValidationError("Total must be an integer, * or left empty") from None


class BaseMseFormSet(forms.BaseFormSet):
    """Form Set for MSE data."""

    def clean(self):
        """Custom validation for MSE data."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        for _form in self.forms:  # TODO: remove the _ when we add this validation
            # TODO: do some kind of validation on the different totals maybe
            pass
