from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    # 管理画面のDBタイトル名
    verbose_name = 'ブログアプリ'
