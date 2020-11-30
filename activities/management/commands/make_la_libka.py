from django.core.management.base import BaseCommand

from activities.models import Activity


class Command(BaseCommand):

    @staticmethod
    def _answer_to_bool(answer: str) -> bool:
        answer_to_bool = {
            "yes": True,
            "y": True,
            "1": True,
            "no": False,
            "n": False,
            "0": False,
        }
        result = answer_to_bool.get(answer.lower())
        if result is None:
            raise ValueError(f"invalid answer: {answer}")
        return result

    def handle(self, **options):
        activity = Activity.objects.first()
        answer = input(f"Should add Libka to activity: {repr(activity)}? [y/n]: ")
        if self._answer_to_bool(answer):
            activity.add_libka()
            print("Libka added to the activity.")
        else:
            print("No action was done.")
