from django.http import HttpResponse
from django.views.generic import TemplateView

from activities.models import Activity, Tag


def index(request):
    return HttpResponse("Hello, world. You're at the activities index.")


class ActivitiesView(TemplateView):
    template_name = 'activities.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mff_tag = Tag.objects.get(name="MFF_misecky")
        years = range(2018, 2019)
        context["years"] = years
        for year in years:
            context[f'activities_{year}'] = Activity.objects.filter(tags__in=[mff_tag], start__year=year)
            print(context[f'activities_{year}'])
        return context
