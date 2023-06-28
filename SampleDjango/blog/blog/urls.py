from django.urls import path

from blog.views import (
    PostListView,
    PostDetailView,
    CategoryPostListView,
    TagPostListView,
    SearchPostListView,
    CommoentCreateView,
    ReplyCreateView,
    CommoentDeleteView,
    ReplyDeleteView,
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('category/<str:slug>/', CategoryPostListView.as_view(), name='category_post_list'),
    path('tag/<str:slug>/', TagPostListView.as_view(), name='tag_post_list'),
    path('search/', SearchPostListView.as_view(), name='search_post_list'),
    path('comment/<int:post_pk>', CommoentCreateView.as_view(), name='comment'),
    path('reply/<int:comment_pk>', ReplyCreateView.as_view(), name='reply'),
    path('comment/<int:pk>/delete/', CommoentDeleteView.as_view(), name='comment_delete'),
    path('reply/<int:pk>/delete', ReplyDeleteView.as_view(), name='reply_delete'),
]