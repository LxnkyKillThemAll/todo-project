from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from datetime import timedelta
import json
from django.utils.timezone import now
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count

# Регистрация пользователя
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')
    else:
        form = UserCreationForm()
    return render(request, 'todoapp/register.html', {'form': form})

# Авторизация пользователя
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'todoapp/login.html', {'form': form})

# Выход из системы
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def task_list(request):
    # Найдем все задачи пользователя
    tasks = Task.objects.filter(user=request.user, is_archived=False)

    # Архивируем просроченные задачи
    now = timezone.now()
    for task in tasks:
        if task.deadline and task.deadline < now and not task.completed:
            task.is_archived = True
            task.save()

    # Обновляем список после архивации
    tasks = Task.objects.filter(user=request.user, is_archived=False).order_by('-important', 'completed', '-deadline')

    # Поиск
    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(title__icontains=query)

    now = timezone.now()
    soon = now + timedelta(hours=24)

    urgent_list = []
    for task in tasks:
        task.is_urgent = False
        if task.deadline and now < task.deadline <= now + timedelta(hours=24) and not task.completed:
            task.is_urgent = True
            urgent_list.append({
                'title': task.title,
                'due': task.deadline.strftime("%d.%m.%Y %H:%M")
            })
    

    return render(request, 'todoapp/task_list.html',
                   {'tasks': tasks,
                    'urgent_tasks': json.dumps(urgent_list, ensure_ascii=False)})

# Создание задачи
@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'todoapp/task_form.html', {'form': form})

# Редактирование задачи
@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todoapp/task_form.html', {'form': form})

# Статискика по задачам
@login_required
def task_stats(request):
    user = request.user
    tasks = Task.objects.filter(user=user, is_archived=False)

    total = tasks.count()
    completed = tasks.filter(completed=True).count()
    important = tasks.filter(important=True).count()
    overdue = tasks.filter(deadline__lt=timezone.now(), completed=False).count()
    upcoming = tasks.filter(deadline__gte=timezone.now(), completed=False).order_by('deadline')[:5]

    context = {
        'total': total,
        'completed': completed,
        'important': important,
        'overdue': overdue,
        'upcoming': upcoming,
    }

    return render(request, 'todoapp/task_stats.html', context)

# Удаление задачи
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'todoapp/task_confirm_delete.html', {'task': task})

@login_required
def archived_tasks(request):
    tasks = Task.objects.filter(user=request.user, is_archived=True)
    return render(request, 'todoapp/archived_tasks.html', {'tasks': tasks})
