from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "presentation/index.html"


class Who(TemplateView):
    template_name = "presentation/who.html"


class Test(TemplateView):
    template_name = "presentation/test.html"


class Faq(TemplateView):
    template_name = "presentation/faq.html"
