from django.shortcuts import render, HttpResponse
from orange_manage import models
from django.db.models import Sum


def user_list(request):
    if request.method == 'GET':
        get_keyword = request.GET.get('keyword', '')
        get_searchtype = request.GET.get('searchtype')
        get_begin_time = request.GET.get('begin_time', '')
        get_end_time = request.GET.get('end_time', '')
        get_status = request.GET.get('status', '2')
        search_data = {
            'keyword': get_keyword,
            'searchtype': get_searchtype,
            'begin_time': get_begin_time,
            'end_time': get_end_time,
            'status': get_status,
        }
        get_pagesize = 15
        get_page = request.GET.get('p', '1')
        start_nun = int(get_pagesize) * (int(get_page) - 1)  # 起始数据位置
        end_num = start_nun + int(get_pagesize)  # 终止数据位置
        get_operator = request.session.get('user')
        obj = models.Admin.objects.filter(account=get_operator).first()
        operator_region = obj.open_admin_region
        if operator_region:
            operator_campus_obj = models.RegionCampus.objects.filter(region_id=operator_region).all()
        else:
            operator_campus_obj = models.RegionCampus.objects.all()
        campus_list = []
        for i in operator_campus_obj:
            campus_list.append(i.campus_id)
        obj = models.User.objects.filter(campus_id__in=campus_list)
        all_money = '%.2f' % obj.values('balance').aggregate(all_money=Sum('balance'))['all_money']
        all_integral = '%.2f' % obj.values('integral').aggregate(all_integral=Sum('integral'))['all_integral']
        disable_money_obj = obj.values('balance').annotate(all_money=Sum('balance')).filter(status=0)
        if disable_money_obj:
            disable_money = 0.0
            for i in disable_money_obj:
                disable_money += i['all_money']
        disable_money = '%.2f' % disable_money
        money_dict = {
            'all_money': all_money,
            'all_integral': all_integral,
            'disable_money': disable_money,
        }
        if len(get_keyword):
            if get_searchtype == 'user_id':
                all_obj = models.User.objects.filter(campus_id__in=campus_list, user_id=get_keyword)
            elif get_searchtype == 'nickname':
                all_obj = models.User.objects.filter(campus_id__in=campus_list, nickname__contains=get_keyword)
            elif get_searchtype == 'phone_number':
                all_obj = models.User.objects.filter(campus_id__in=campus_list, phone_number__contains=get_keyword)
        else:
            all_obj = models.User.objects.filter(campus_id__in=campus_list)
        if get_status != '2': all_obj = all_obj.filter(status=get_status)
        if len(get_begin_time) and len(get_end_time):
            all_obj = all_obj.filter(register_time__gte=get_begin_time)
            all_obj = all_obj.filter(register_time__lte=get_end_time)
        if len(all_obj) % int(get_pagesize):
            page_total = len(all_obj) // int(get_pagesize) + 1
        else:
            page_total = len(all_obj) // int(get_pagesize)
        data_list = []
        for i in all_obj[start_nun:end_num]:
            data_dict = {
                'user_id': i.user_id,
                'nickname': i.nickname,
                'username': i.username,
                'phone_number': i.phone_number,
                'last_ip': i.last_ip,
                'last_login': i.last_login,
                'status': i.status,
                'balance': i.balance,
                'integral': i.integral,
            }
            data_list.append(data_dict)
        return render(request, 'User/index.html',
                      {'data': data_list, 'money_data': money_dict, 'get_page': get_page, 'page_total': str(page_total),
                       'search_data': search_data})


def user_edit(request):
    if request.method=='GET':
        get_userid=request.GET.get('userid')
        obj=models.User.objects.get(user_id=get_userid)
        data={
            'ID':get_userid,
            'nickname':obj.nickname,
            'username':obj.username,
            'name':obj.name,
            'gender':obj.gender,
            'phone_number':obj.phone_number,
            'qq':obj.qq,
            'campus_id':obj.campus_id,
            'register_time':obj.register_time,
            'last_login':obj.last_login,
            'status':obj.status,
            'balance':obj.balance,
            'integral':obj.integral,
            'last_ip':obj.last_ip,
        }
        return render(request,'User/edit.html',{'data':data})
    elif request.method=='POST':
        get_userid=request.GET.get('userid')
        get_status=request.GET.get('status')
        models.User.objects.filter(user_id=get_userid).update(status=get_status)
        return HttpResponse(1)