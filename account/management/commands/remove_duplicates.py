from django.core.management.base import BaseCommand
from home.models import Karamooz




class Command(BaseCommand):
    help = "Remove duplicate Karamooz records based on code (شماره پروانه). Keeps only the first record."

    def handle(self, *args, **options):
        seen = set()
        duplicates = []

        for obj in Karamooz.objects.all().order_by('id'):
            # معیار یکتا بودن: شماره پروانه
            key = obj.code

            if key in seen:
                duplicates.append(obj.id)
            else:
                seen.add(key)

        if duplicates:
            count = len(duplicates)
            Karamooz.objects.filter(id__in=duplicates).delete()
            self.stdout.write(self.style.SUCCESS(f"{count} رکورد تکراری حذف شد."))
        else:
            self.stdout.write(self.style.WARNING("هیچ رکورد تکراری پیدا نشد."))
