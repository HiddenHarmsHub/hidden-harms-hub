import os
import shutil
from itertools import combinations
from tempfile import TemporaryDirectory

from celery.result import AsyncResult
from django.conf import settings
from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse
from django.views import View
from django.views.generic.edit import FormView

from general.forms import BaseMseFormSet, MseDetailsForm, MseExamplesForm, MseForm, MseOptionsForm, MseSetupForm
from general.models import TempMseUpload
from general.tasks import calculate_mse


class MultipleSystemsEstimationSetup(FormView):
    """Setup the MSE form."""

    template_name = "general/mse_setup.html"
    success_url = "/multiplesystemsestimation/calculator"
    form_class = MseSetupForm

    def form_valid(self, form):
        """Store the data in the session.

        Args:
            form (general.forms.MseSetupForm): The form for the MSE setup.

        Returns:
            HttpResponse: A redirect to the success_url.
        """
        if form.cleaned_data["total_lists_required"] is not None:
            self.request.session["mode"] = "new"
            self.request.session["total_lists_required"] = form.cleaned_data["total_lists_required"]
        else:
            self.request.session["mode"] = "upload"
            csv_file = form.cleaned_data["file_upload"]
            temp_file = TempMseUpload.objects.create(file=csv_file)
            self.request.session["upload_id"] = temp_file.id
        return super().form_valid(form)


class MultipleSystemsEstimationExamplesView(FormView):
    """Allow example selection and save choice in session."""

    template_name = "general/mse_examples.html"
    success_url = "/multiplesystemsestimation/calculator"
    form_class = MseExamplesForm

    def form_valid(self, form):
        """Store the data in the session.

        Args:
            form (general.forms.MseExamplesForm): The form for the MSE example choices.

        Returns:
            HttpResponse: A redirect to the success_url.
        """
        self.request.session["mode"] = "example"
        self.request.session["example"] = form.cleaned_data["example"]
        return super().form_valid(form)


class MultipleSystemsEstimation(FormView):
    """Process the MSE data."""

    on_success = "multiplesystemsestimation/calculator"

    def _calculate_initial_data(self, total_lists):
        """Calculate all of the list combinations and return the list of lists and the combinations.

        Also records whether a combination is the first of its type (i.e. the first of the pairs or the first of
        the triples) so that a divider can be placed on the table to assist with the data entry.

        Args:
            total_lists (int): The total number of lists in the data.

        Returns:
            tuple: A tuple containing two lists, the first a list of each of the data lists, the second a list of
                dictionaries containing list combinations whether they are the first of their type or not.
        """
        lists = []
        initial = []  # reset this in case of reposts
        for number in range(1, total_lists + 1):
            lists.append(f"list {number}")
        list_combos = [[[x] for x in lists]]
        for combination_size in range(2, total_lists + 1):
            list_combos.append([list(x) for x in list(combinations(lists, combination_size))])
        for typ in list_combos:
            for i, item in enumerate(typ):
                if len(item) > 1 and i == 0:
                    initial.append({"required_lists": item, "first": True})
                else:
                    initial.append({"required_lists": item, "first": False})
        return lists, initial

    def _add_uploaded_totals(self, initial, rows, lists):
        """Add the total_appearances data to the initial data in the case where this has been uploaded via a file.

        Args:
            initial (list): A list of dictionaries containing the initial data to use in the forms without the uploaded
                totals.
            rows (list): A list where each entry is one row of the input file.
            lists (list): A list of each of the individual lists included in the data.

        Returns:
            list: The initial data to use in the forms with the uploaded totals added.
        """
        censoring_settings = {}
        if len(rows[0].split(",")) == 1:  # then we have censoring settings to separate out
            censoring_lower = rows[0]
            censoring_upper = rows[1]
            censoring_settings = {"censoring_lower": censoring_lower, "censoring_upper": censoring_upper}
            rows = rows[2:]
        for entry in initial:
            expected = ",".join(["1" if x in entry["required_lists"] else "0" for x in lists])
            for row in rows:
                if row.startswith(f"{expected},"):
                    entry["total_appearances"] = row.split(",")[-1].replace("\n", "")
        return initial, censoring_settings

    def get(self, request):
        """Display the required form/data if the required session data is available or redirect if not.

        Args:
            request (django.http.HttpRequest): The current request.

        Returns:
            HttpResponseRedirect: A redirect to the first page in the MSE workflow.

        Raises:
            Exception: Raised if the file path is not safe (extremely unlikely).
        """
        if "mode" not in request.session:
            return HttpResponseRedirect(reverse("general:mse"))
        if request.session["mode"] not in ["new", "upload", "example"]:
            return render(request, "general/mse_error.html")
        MseFormSet = formset_factory(MseDetailsForm, formset=BaseMseFormSet, extra=0)  # NoQA
        if request.session["mode"] == "new":
            try:
                censoring_settings = []
                total_lists = int(request.session["total_lists_required"])
                lists, initial = self._calculate_initial_data(total_lists)
                request.session.pop("total_lists_required", None)
            except Exception:
                request.session.pop("mode", None)
                request.session.pop("total_lists_required", None)
                return render(request, "general/mse_error.html")
        elif request.session["mode"] == "upload":
            try:
                file_id = self.request.session["upload_id"]
                temp_file = TempMseUpload.objects.get(id=file_id)
                contents = temp_file.file.read().decode("utf-8")
                rows = contents.split("\n")
                if len(rows) >= 3:
                    total_lists = len(rows[2].split(",")) - 1
                else:
                    total_lists = len(rows[0].split(",")) - 1
                lists, initial = self._calculate_initial_data(total_lists)
                initial, censoring_settings = self._add_uploaded_totals(initial, rows, lists)
                request.session.pop("upload_id", None)
            except Exception:
                request.session.pop("mode", None)
                request.session.pop("upload_id", None)
                return render(request, "general/mse_error.html")
        elif request.session["mode"] == "example":
            try:
                safe_file = request.session["example"]
                file_path = os.path.abspath(os.path.join(settings.EXAMPLES_ROOT, f"{safe_file}.csv"))
                if file_path.startswith(settings.EXAMPLES_ROOT):
                    safe_path = file_path
                else:
                    raise Exception()
                with open(safe_path) as example_file:
                    contents = example_file.read()
                rows = contents.split("\n")
                if len(rows) >= 3:
                    total_lists = len(rows[2].split(",")) - 1
                else:
                    total_lists = len(rows[0].split(",")) - 1
                lists, initial = self._calculate_initial_data(total_lists)
                initial, censoring_settings = self._add_uploaded_totals(initial, rows, lists)
                request.session.pop("example", None)
            except Exception:
                request.session.pop("mode", None)
                request.session.pop("example", None)
                return render(request, "general/mse_error.html")
        request.session.pop("mode", None)
        form = MseForm(initial={"total_lists": total_lists})
        options_form = MseOptionsForm(initial=censoring_settings)
        formset = MseFormSet(initial=initial)
        data = {"formset": formset, "form": form, "options_form": options_form, "lists": lists}
        return render(request, "general/mse_calculator.html", data)

    def post(self, request):
        """Handle submission of the MSE data and trigger the task to run the calculation.

        Args:
            request (django.http.HttpRequest): The current request.

        Returns:
            HttpResponse: The appropriate page which will be the results page in loading mode or a redirect if the
                data was not valid.
        """
        MseFormSet = formset_factory(MseDetailsForm, formset=BaseMseFormSet, extra=0)  # NoQA

        total_lists = int(request.POST.get("total_lists"))
        lists, initial = self._calculate_initial_data(total_lists)
        formset = MseFormSet(
            request.POST.get("censoring_lower"), request.POST.get("censoring_upper"), request.POST, initial=initial
        )
        options_form = MseOptionsForm(request.POST)
        if not formset.is_valid():
            form = MseForm(initial={"total_lists": total_lists})
            data = {"formset": formset, "form": form, "options_form": options_form, "lists": lists}
            return render(request, "general/mse_calculator.html", data)
        # prepare the data
        appearance_data = []
        for form in formset:
            row_data = form.cleaned_data
            if row_data["total_appearances"] == "*":
                appearance_data.append(-1)
            else:
                appearance_data.append(int(row_data["total_appearances"]))
        mse_input = {
            "list_data": appearance_data,
            "censoring_lower": int(request.POST.get("censoring_lower")),
            "censoring_upper": int(request.POST.get("censoring_upper")),
            "total_lists": total_lists,
            "model_type": request.POST.get("model_type"),
        }
        # run the calculation
        task = calculate_mse.delay(mse_input)
        # prepare the data for the download
        stringified_data = [f"{mse_input['censoring_lower']}|||{mse_input['censoring_upper']}|||"]
        for form in formset:
            row_data = form.cleaned_data
            for list_name in lists:
                if list_name in row_data["required_lists"]:
                    stringified_data.append(f"{1}|")
                else:
                    stringified_data.append(f"{0}|")
            if row_data["total_appearances"] == "":
                total_appearances = "-"
            else:
                total_appearances = row_data["total_appearances"]
            stringified_data.append(f"{total_appearances}|||")
        csv_data = "".join(stringified_data)
        data = {
            "formset": formset,
            "options_form": options_form,
            "lists": lists,
            "results_display": True,
            "csv_data": csv_data,
            "task_id": task.task_id,
        }
        return render(request, "general/mse_calculator.html", data)


class MultipleSystemsEstimationDownload(View):
    """Download the results and the input data."""

    def post(self, request):
        """Create and download a zipfile of the results and data, or just the data if there was an error.

        Args:
            request (django.http.HttpRequest): The current request.

        Returns:
            HttpResponse: A zip file download of the results and the input data.
        """
        temp_dir = TemporaryDirectory()
        output_path = os.path.join(temp_dir.name, "export")
        os.makedirs(output_path)
        results = request.POST.get("results")
        if results != "failed":
            if request.POST.get("model_type") == "NPE":
                summary, samples = results.split("|")
                with open(os.path.join(output_path, "summary.csv"), mode="w") as result_file:
                    result_file.write(summary)
                with open(os.path.join(output_path, "samples.csv"), mode="w") as result_file:
                    result_file.write(samples)
            else:
                with open(os.path.join(output_path, "results.csv"), mode="w") as result_file:
                    result_file.write(results)
        with open(os.path.join(output_path, "mse_input.csv"), mode="w") as input_file:
            data = request.POST.get("csv-data")
            lines = data.split("|||")
            for line in lines:
                input_file.write(line.replace("|", ",").replace("-", ""))
                input_file.write("\n")
        if results == "failed":
            filename = "mse_input"
        else:
            filename = "mse_results"
        filepath = os.path.join(temp_dir.name, filename)
        shutil.make_archive(filepath, "zip", os.path.join(temp_dir.name, "export"))
        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=" + filename
        response.write(open(f"{filepath}.zip", "rb").read())
        return response


def poll_state(request):
    """Check the current state of a task.

    Args:
        request (django.http.HttpRequest): The current request.

    Returns:
        JsonResponse: The current state of the task.
    """
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if "task_id" in request.POST.keys() and request.POST["task_id"]:
            task_id = request.POST["task_id"]
            task = AsyncResult(task_id)
            if isinstance(task.result, Exception):
                context = {"data": {"message": str(task.result)}, "state": task.state}
            else:
                context = {"data": task.result, "state": task.state}
        else:
            context = {"data": "No task_id in the request", "state": "FAILURE"}
    else:
        context = {"data": "This is not an ajax request", "state": "FAILURE"}

    return JsonResponse(context)
