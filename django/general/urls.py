from django.urls import path
from django.views.generic import TemplateView

from general import views

app_name = 'general'
urlpatterns = [
    path("", TemplateView.as_view(template_name="general/home.html"), name="home"),
    path("cookies/", TemplateView.as_view(template_name="general/cookies.html"), name="cookies"),
    path('pollstate', views.poll_state, name="pollstate"),
    path("comparativejudgement", TemplateView.as_view(template_name="general/comparative_judgement.html"), name="cj"),
    path(
        "multiplesystemsestimation/examples",
        TemplateView.as_view(template_name="general/mse_examples.html"),
        name="mseexamples"
    ),
    path(
        "multiplesystemsestimation/calculator",
        views.MultipleSystemsEstimation.as_view(),
        name="mse_calc"
    ),
    path(
        "multiplesystemsestimation/download",
        views.MultipleSystemsEstimationDownload.as_view(),
        name="mse_download"
    ),
    path(
        "multiplesystemsestimation",
        TemplateView.as_view(template_name="general/multiple_systems_estimation.html"),
        name="mse",
    ),
]
