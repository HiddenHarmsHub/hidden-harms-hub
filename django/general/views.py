from itertools import combinations

from django.forms import formset_factory
from django.shortcuts import render
from django.views.generic.edit import FormView

from general.forms import BaseMseFormSet, MseDetailsForm, MseForm, MseSetupForm


class MultipleSystemsEstimationSetup(FormView):
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
        data = {
            "formset": formset,
            "lists": lists,
            "results": results,
            "results_display": True,
        }
        return render(request, "general/mse_calculator.html", data)
        # response = HttpResponse(content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename=' + filename
        # response.write(open(filepath, 'rb').read())
        # return response
