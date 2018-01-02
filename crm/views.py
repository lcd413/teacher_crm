from django.shortcuts import render,redirect
from rbac import models
from rbac.service.init_permission import init_permission
# Create your views here.
def login(request):
    if request.method=='GET':
        return render(request,'login.html')
    else:
        user=request.POST.get('username')
        pwd=request.POST.get('password')
        user=models.User.objects.filter(username=user,password=pwd).first()
        if user:
            request.session['user_info'] = {'user_id': user.id, 'uid': user.userinfo.id, 'name': user.userinfo.name}
            init_permission(user, request)
            return redirect('/index/')
        return render(request, 'login.html')
def index(request):
    return render(request,'index.html')
