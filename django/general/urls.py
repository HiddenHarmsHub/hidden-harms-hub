from django.urls import path
from django.views.generic import TemplateView

from general import views

app_name = 'general'
urlpatterns = [
    path("", TemplateView.as_view(template_name="general/home.html"), name="home"),
    path("cookies/", TemplateView.as_view(template_name="general/cookies.html"), name="cookies"),
    path("comparativejudgement", TemplateView.as_view(template_name="general/comparative_judgement.html"), name="cj"),
     path(
        "multiplesystemsestimation/calculator",
        views.MultipleSystemsEstimationSetup.as_view(),
        name="mse_calc"
    ),
    path(
        "multiplesystemsestimation",
        TemplateView.as_view(template_name="general/multiple_systems_estimation.html"),
        name="mse",
    ),
]
