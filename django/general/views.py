import os
import shutil
from itertools import combinations
from tempfile import TemporaryDirectory

from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView

from general.forms import BaseMseFormSet, MseDetailsForm, MseForm, MseSetupForm


class MultipleSystemsEstimation(FormView):
    """Setup and process the MSW data."""
    on_success = "multiplesystemsestimation/calculator"

    def _calculate_initial_data(self, total_lists):
        lists = []
        initial = []  # reset this in case of reposts
        for i in range(0, total_lists):
            lists.append(f'list {i + 1}')
        list_combos = [[[x] for x in lists]]
        for i in range(1, total_lists):
            list_combos.append([list(x) for x in list(combinations(lists, i + 1))])
        for typ in list_combos:
            for i, item in enumerate(typ):
                if len(item) > 1 and i == 0:
                    initial.append({'required_lists': item, 'first': True})
                else:
                    initial.append({'required_lists': item, 'first': False})
        return lists, initial

    def get(self, request):
        """Display the MSE setup page.

        Args:
            request (django.http.HttpRequest): The current request.

        Returns:
            HttpResponse: The MSE setup page.
        """
        form = MseSetupForm
        return render(request, "general/mse_setup.html", {"form": form})

    def post(self, request):
        """Handle submission, part 2 of the MSE form display and displaying the results.

        Args:
            request (django.http.HttpRequest): The current request.

        Returns:
            HttpResponse: The appropriate page for the stage of the process.
        """
        MseFormSet = formset_factory(MseDetailsForm, formset=BaseMseFormSet, extra=0)  # NoQA
        if "total_lists_required" in request.POST:
            total_lists = int(request.POST.get("total_lists_required"))
            # render part 2 of the form
            lists, initial = self._calculate_initial_data(total_lists)
            form = MseForm(initial={"total_lists": total_lists})
            formset = MseFormSet(initial=initial)
            return render(request, "general/mse_calculator.html", {"formset": formset, "form": form, "lists": lists})
        total_lists = int(request.POST.get("total_lists"))
        lists, initial = self._calculate_initial_data(total_lists)
        formset = MseFormSet(request.POST, initial=initial)
        if not formset.is_valid():
            return render(request, "general/mse_calculator.html", {"formset": formset, "lists": lists})

        results = 'These are the results of your MSE'
        stringified_data = []
        for form in formset:
            row_data = form.cleaned_data
            for list_name in lists:
                if list_name in row_data["required_lists"]:
                    stringified_data.append(f"{1}|")
                else:
                    stringified_data.append(f"{0}|")
            stringified_data.append(f"{row_data['total_appearances']}|||")
        csv_data = "".join(stringified_data)
        data = {
            "formset": formset,
            "lists": lists,
            "results": results,
            "results_display": True,
            "csv_data": csv_data,
        }
        return render(request, "general/mse_calculator.html", data)


class MultipleSystemsEstimationDownload(View):
    """Download the results and the input data."""

    def post(self, request):
        """Create and download a zipfile of the results and data.

        Args:
            request (django.http.HttpRequest): The current request.

        Returns:
            HttpResponse: A zip file download of the results and the input data.
        """
        temp_dir = TemporaryDirectory()
        output_path = os.path.join(temp_dir.name, "export")
        os.makedirs(output_path)
        with open(os.path.join(output_path, "results.txt"), mode="w") as result_file:
            result_file.write(request.POST.get("results"))
        with open(os.path.join(output_path, "mse_input.txt"), mode="w") as input_file:
            data = request.POST.get("csv-data")
            lines = data.split("|||")
            for line in lines:
                input_file.write(line.replace("|", "\t"))
                input_file.write("\n")

        filename = "mse_results"
        filepath = os.path.join(temp_dir.name, filename)
        shutil.make_archive(filepath, "zip", os.path.join(temp_dir.name, "export"))
        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=" + filename
        response.write(open(f"{filepath}.zip", "rb").read())
        return response
