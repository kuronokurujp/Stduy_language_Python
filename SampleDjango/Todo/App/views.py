from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView
)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from App.models import Task

# Todoリストビュー
class TodoListView(ListView):
    model = Task
    template_name = 'Task/TaskList.html'

# Todo詳細ビュー
class TodoDetailView(DetailView):
    model = Task
    template_name = 'Task/TaskDetail.html'

# Todo作成ビュー
class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = '__all__'
    template_name = 'Task/TaskForm.html'
    success_url = reverse_lazy('task_list')
    
# Todo削除ビュー
class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'Task/TaskDelete.html'
    success_url = reverse_lazy('task_list')

# Todo編集ビュー
class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = '__all__'
    template_name = 'Task/TaskForm.html'
    success_url = reverse_lazy('task_list')
