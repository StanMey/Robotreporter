from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import UserRegisterForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Checks for validity of the new user
            form.cleaned_data
            user_name = form.save()
            # set the new user in the "view_only" group
            group = Group.objects.get(name="view_only")
            user = User.objects.get(username=user_name)
            group.user_set.add(user)

            messages.success(request, "Your account has been created! You are now able to log in")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html')
