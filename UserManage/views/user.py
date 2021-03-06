#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from website.common.CommonPaginator import SelfPaginator
from UserManage.views.permission import PermissionVerify

from django.contrib import auth
from django.contrib.auth import get_user_model
from UserManage.forms import LoginUserForm,ChangePasswordForm,AddUserForm,EditUserForm
from Audit.common import Login_re
from Asset.common import write_excel

def LoginUser(request):
    '''用户登录view'''
    if request.user.is_authenticated():
              return HttpResponseRedirect('/')

    if request.method == 'GET' and request.GET.has_key('next'):
        next = request.GET['next']
    else:
        next = '/'
    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
	    Login_re(request)
	    if request.user.username == "admin":
               return HttpResponseRedirect(request.POST['next'])
            else:
               return HttpResponseRedirect(reverse('index_cu'))
    else:
        form = LoginUserForm(request)
    kwvars = {
        'request':request,'form':form,'next':next,
    }
    return render_to_response('UserManage/login.html',kwvars,RequestContext(request))

@login_required
def LogoutUser(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def ChangePassword(request):
    kwvars = {'request':request}
    if request.method=='POST':
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            kwvars['form'] = form
	    kwvars['msg'] = "修改成功,请退出重新登录!"
            return render_to_response('UserManage/password.change.html',kwvars,RequestContext(request))
            #return HttpResponseRedirect(reverse('logouturl'))
    else:
        form = ChangePasswordForm(user=request.user)
    kwvars['form'] = form
    return render_to_response('UserManage/password.change.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def ListUser(request):
    search = request.GET.get('keyword','')
    export = request.GET.get('export','')
    kwvars = {'request':request,'URL':'listuserurl'}
    if(len(search)!=0):
        mList = get_user_model().objects.filter(username__contains=search)
    else:
        mList = get_user_model().objects.all()
    if export:
       try:
          rev = write_excel(mList,user=request.user.username,T="user")
          return rev
       except Exception,e:
         kwvars["err"] = "导出列表错误!%s"%(str(e))
         return render_to_response('status.html',kwvars,RequestContext(request))

    lst = SelfPaginator(request,mList, 20)
    kwvars['lPage'] = lst
    return render_to_response('UserManage/user.list.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def AddUser(request):
    if request.method=='POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            form.save()
            return HttpResponseRedirect(reverse('listuserurl'))
    else:
        form = AddUserForm()
    kwvars = {
        'form':form,
        'request':request,
    }
    return render_to_response('UserManage/user.add.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def EditUser(request,ID):
    user = get_user_model().objects.get(id = ID)
    if request.method=='POST':
        form = EditUserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('listuserurl'))
    else:
        form = EditUserForm(instance=user
        )
    kwvars = {
        'ID':ID,
        'form':form,
        'request':request,
    }
    return render_to_response('UserManage/user.edit.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def DeleteUser(request,ID):
    if ID == '1':
        return HttpResponse(u'超级管理员不允许删除!!!')
    else:
        get_user_model().objects.filter(id = ID).delete()

    return HttpResponseRedirect(reverse('listuserurl'))

@login_required
@PermissionVerify()
def ResetPassword(request,ID):
    user = get_user_model().objects.get(id = ID)
    newpassword = get_user_model().objects.make_random_password(length=10,allowed_chars='abcdefghjklmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY3456789')
    print '====>ResetPassword:%s-->%s' %(user.username,newpassword)
    user.set_password(newpassword)
    user.save()
    kwvars = {
        'object':user,
        'newpassword':newpassword,
        'request':request,
    }
    return render_to_response('UserManage/password.reset.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def Mdel(request):
    ids = request.GET.get('ids')
    ids = ids.split(',')
    for Id in ids:
         if Id == '1':
            return HttpResponse(u'超级管理员不允许删除!!!')
         else:
            get_user_model().objects.filter(id = Id).delete()
    return HttpResponse('删除成功')

@login_required
@PermissionVerify()
def Details(request,ID):
    iu = get_user_model().objects.get(id = ID)
    kwvars = {'i':iu,'request':request}
    return render_to_response('UserManage/user.details.html',kwvars,RequestContext(request))

@login_required
def Info(request):
    iu = get_user_model().objects.get(username = request.user.username)
    kwvars = {'i':iu,'request':request}
    return render_to_response('UserManage/user.details.html',kwvars,RequestContext(request))
