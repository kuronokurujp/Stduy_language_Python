from django.db.models import Count, Q
from blog.models import Category, Tag

def common(request):
    context = {
        # カテゴリーモデルからオブジェクトリストを取得して設定
        # その時にカテゴリーの公開用フラグがTrueの数を変数を追加している
        "categories": Category.objects.annotate(
            count = Count('post', Q(post__is_published=True))
        ),
        'tags': Tag.objects.all()
    }
    
    return context