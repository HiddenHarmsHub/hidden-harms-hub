from django import forms
from django.core.exceptions import ValidationError


class MseSetupForm(forms.Form):
    """Form to setup the MSE main form."""
    total_lists_required = forms.IntegerField(required=False)
    file_upload = forms.FileField(required=False)


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
            ValidationError: raised if the data is not valid.
        """
        total = self.cleaned_data.get("total_appearances")
        if total != "*":
            try:
                int(total)
            except ValueError:
                raise ValidationError("Total must be an integer or * (* is used for censored data)") from None


class MseOptionsForm(forms.Form):
    """Form to collect the additional processing options required."""
    censoring_lower = forms.ChoiceField(choices=[(x, x) for x in range(0, 2)])
    censoring_upper = forms.ChoiceField(choices=[(x, x) for x in range(0, 11)])


class BaseMseFormSet(forms.BaseFormSet):
    """Form Set for MSE data."""
    def __init__(self, censoring_lower=0, censoring_upper=0, *args, **kwargs):
        self._censoring_upper = int(censoring_upper)
        self._censoring_lower = int(censoring_lower)
        super().__init__(*args, **kwargs)

    def clean(self):
        """Custom validation for MSE data.

        Raises:
            ValidationError: raised if a * is used if the censoring upper value is 0.
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        if self._censoring_upper == 0:
            # then we are not allowed * entries
            for form in self.forms:
                if form.cleaned_data.get("total_appearances") == "*":
                    raise ValidationError("Censoring upper must be greater than 0 if * is used in the data.")
        if self._censoring_upper > 0:
            # then we must have at least one * entry and we are not allowed any values between censoring_lower and
            # censoring_upper
            has_star = False
            for form in self.forms:
                total_appearances = form.cleaned_data.get("total_appearances")
                if total_appearances == "*":
                    has_star = True
                elif (
                    int(total_appearances) >= self._censoring_lower and int(total_appearances) <= self._censoring_upper
                ):
                    raise ValidationError(
                        "No values can fall in the censored range if censoring upper is greater than 0."
                    )
            if not has_star:
                raise ValidationError(
                    "If censoring upper is greater than 0 then some entries need to be censored with *."
                )
