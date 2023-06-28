from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

# カテゴリのモデル
# 複数の記事モデルと関係を持つ
class Category(models.Model):
    name = models.CharField(verbose_name='カテゴリー', max_length=255)
    # urlとして利用する。urlとして利用するので重複しないようにユニーク設定をしている
    slug = models.SlugField(verbose_name='URL', unique=True)
    
    def __str__(self):
        return self.name
    
    # 管理画面のタイトル名など変えている
    class Meta:
        verbose_name = 'カテゴリー'
        verbose_name_plural = 'カテゴリー'

# タグのモデル
class Tag(models.Model):
    name = models.CharField(verbose_name='タグ', max_length=255)
    # urlとして利用する。urlとして利用するので重複しないようにユニーク設定をしている
    slug = models.SlugField(verbose_name='URL', unique=True)

    def __str__(self):
        return self.name

    # 管理画面のタイトル名など変えている
    class Meta:
        verbose_name = 'タグ'
        verbose_name_plural = 'タグ'

# ブログの記事モデル
# １つのカテゴリモデルとの関係を持つ
class Post(models.Model):
    title = models.CharField(verbose_name='記事のタイトル', max_length=200)
#    content = models.TextField(verbose_name='記事の本分')
    content = MarkdownxField(verbose_name='記事の本分')
    image = models.ImageField(verbose_name='画像', upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    is_published = models.BooleanField(verbose_name="公開設定", default=False)
    
    # 記事が複数に対してカテゴリーは1なので
    # カテゴリと記事は1(カテゴリー)体多(記事)の関係
    # カテゴリのモデルを親として紐づける
    # カテゴリに紐づいた記事が残っている場合はカテゴリを削除できないようにPROTECTをしている
    category = models.ForeignKey(Category, verbose_name='カテゴリー', on_delete=models.PROTECT, null=True, blank=True)
    
    # タグと記事の関係は多対多
    tags = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)
    
    def convert_markdown_to_html(self):
        return markdownify(self.content)

    def __str__(self):
        return self.title

    # 管理画面のタイトル名など変えている
    class Meta:
        verbose_name = '記事'
        verbose_name_plural = '記事'

# コメントモデル
class Comment(models.Model):
    name = models.CharField(verbose_name='名前', max_length=100)
    text = models.TextField(verbose_name='本文')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    
    # 記事削除と同時にコメントデータも削除
    post = models.ForeignKey(Post, verbose_name='記事', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # 管理画面のタイトル名など変えている
    class Meta:
        verbose_name = 'コメント'
        verbose_name_plural = 'コメント'

# コメント返信モデル
class Reply(models.Model):
    name = models.CharField(verbose_name='名前', max_length=100)
    text = models.TextField(verbose_name='本文')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    
    # 記事削除と同時にコメントデータも削除
    comment = models.ForeignKey(Comment, verbose_name='コメント', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

    # 管理画面のタイトル名など変えている
    class Meta:
        verbose_name = '返信'
        verbose_name_plural = '返信'
