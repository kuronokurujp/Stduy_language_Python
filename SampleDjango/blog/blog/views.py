from django.db.models import Q
from typing import Any, Dict, Optional
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    Http404,
    HttpResponse
)

from django.urls import reverse_lazy, reverse
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView
)

from blog.models import (
    Post,
    Category,
    Tag,
    Comment,
    Reply
)

from blog.forms import (
    CommentForm,
    ReplyForm
)

posts_per_page = 5

# ブログリスト
class PostListView(ListView):
    template_name = 'blog/post_list.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = posts_per_page
    
    def get_queryset(self) -> QuerySet[Any]:
        post = super().get_queryset()
        # 更新時間日付の降順ソートする
        return post.order_by('-updated_at')
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        return context

# プログ詳細
class PostDetailView(DetailView):
    template_name = 'blog/post_detail.html'
    model = Post
    
    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        if post.is_published or self.request.user.is_authenticated:
            return post
        else:
            return Http404('Page not found')

# カテゴリーポストリスト
class CategoryPostListView(ListView):
    template_name = 'blog/post_list.html'
    model = Post
    # テンプレートから取得するオブジェクト名を変える
    context_object_name = 'posts'
    paginate_by = posts_per_page

    def get_queryset(self):
        # このクラスにはどんなプロパティがあってその中身は何かを調べるのに以下の方法が役に立つ
        # print(vars(self))
        # カテゴリーのURLの末尾の文字列を取得
        slug = self.kwargs['slug']
        # カテゴリーデータがあるかslugでチェック
        # なければ404エラーを返す
        self.category = get_object_or_404(Category, slug=slug)

        # モデルがPostなのでPostの中にあるcategoryデータでslugと一致するカテゴリーデータを要求
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        # テンプレートに渡すオブジェクトを追加
        context['category'] = self.category
        # 書式を整えて出力してくれる
        # from pprint import pprint
        # pprint(context)
        return context

# タグポストリスト
class TagPostListView(ListView):
    template_name = 'blog/post_list.html'
    model = Post
    # テンプレートから取得するオブジェクト名を変える
    context_object_name = 'posts'
    paginate_by = posts_per_page
    
    def get_queryset(self):
        # タグURLの末尾の文字列を取得
        # print(vars(self))
        slug = self.kwargs['slug']
        # タグデータがあるかslugでチェック
        # なければ404エラーを返す
        self.tags = get_object_or_404(Tag, slug=slug)
        
        # モデルがPostなのでPostの中にあるcategoryデータでslugと一致するカテゴリーデータを要求
        return super().get_queryset().filter(tags=self.tags)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        # テンプレートに渡すオブジェクトを追加
        context['tag'] = self.tags
        return context

# 検索結果のポストリスト
class SearchPostListView(ListView):
    template_name = 'blog/post_list.html'
    model = Post
    # テンプレートから取得するオブジェクト名を変える
    context_object_name = 'posts'
    paginate_by = posts_per_page
    
    def get_queryset(self):
        self.query = self.request.GET.get('query') or ""
        queryset = super().get_queryset()
        
        # ブログのタイトルと本文で検索
        if self.query:
            queryset = queryset.filter(
                Q(title__icontains=self.query) |
                Q(content__icontains=self.query)
            )
            
        # ログインしていない状態では公開記事のみ取得する
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True)
            
        self.post_count = queryset.count
        
        return queryset

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['post_count'] = self.post_count

        return context

# コメント用のView
class CommoentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        
        post_pk = self.kwargs['post_pk']
        post = get_object_or_404(Post, pk=post_pk)
        
        comment.post = post
        comment.save()

        return redirect('post_detail', pk=post_pk)
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        post_pk = self.kwargs['post_pk']
        
        context['post'] = get_object_or_404(Post, pk=post_pk)
        
        return context

# 返信用のView
class ReplyCreateView(CreateView):
    model = Reply 
    form_class = ReplyForm
    template_name = 'blog/comment_form.html'
    
    def form_valid(self, form):
        reply = form.save(commit=False)
        
        comment_pk = self.kwargs['comment_pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        
        reply.comment = comment
        reply.save()

        return redirect('post_detail', pk=comment.post.pk)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        comment_pk = self.kwargs['comment_pk']
        
        context['comment'] = get_object_or_404(Comment, pk=comment_pk)
        
        return context

# コメント削除のView
class CommoentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_delete.html'
    
    # 削除成功後に記事詳細の遷移
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})

# 返信削除のView
class ReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = 'blog/comment_delete.html'
    
    # 削除成功後に記事詳細の遷移
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.comment.post.pk})
