from django.urls import path

from App.views import (
    TodoListView,
    TodoDetailView,
    TodoCreateView,
    TodoDeleteView,
    TodoUpdateView
)

urlpatterns = [
    path('', TodoListView.as_view(), name='task_list'),
    path('Task/New', TodoCreateView.as_view(), name='task_new'),
    # タスク情報のid値をurlに含める
    path('Task/<int:pk>', TodoDetailView.as_view(), name='task_detail'),
    path('Task/<int:pk>/Delete', TodoDeleteView.as_view(), name='task_delete'),
    path('Task/<int:pk>/Edit', TodoUpdateView.as_view(), name='task_update'),
]
