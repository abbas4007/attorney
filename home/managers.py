from django.db import models  # مطمئن شو این خط هست

class ArticleManager(models.Manager):
    def published(self) :
        return self.filter(status = 'p').order_by('-publish', '-created')

