from django.core.management.base import BaseCommand
from home.models import Karamooz


class Command(BaseCommand):
    help = "Find duplicate Karamooz records (بر اساس شماره پروانه) و فقط گزارش می‌دهد."

    def handle(self, *args, **options):
        seen = set()
        duplicates = []

        for obj in Karamooz.objects.all().order_by('id'):
            key = obj.code  # معیار یکتایی
            if key in seen:
                duplicates.append(obj)
            else:
                seen.add(key)

        if duplicates:
            self.stdout.write(self.style.WARNING(
                f"{len(duplicates)} رکورد تکراری پیدا شد."
            ))
            for dup in duplicates[:20]:  # فقط 20 رکورد اول برای نمایش
                self.stdout.write(
                    f"ID={dup.id}, name={dup.name}, lastname={dup.lastname}, code={dup.code}"
                )
            if len(duplicates) > 20:
                self.stdout.write("... بقیه رکوردهای تکراری نمایش داده نشدند.")
        else:
            self.stdout.write(self.style.SUCCESS("هیچ رکورد تکراری پیدا نشد."))
