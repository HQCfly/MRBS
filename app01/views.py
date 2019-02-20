from django.shortcuts import render,redirect,HttpResponse

# Create your views here.

from django.contrib import auth


def login(request):

    if request.method=="POST":
        user=request.POST.get("user")
        pwd=request.POST.get("pwd")

        user=auth.authenticate(username=user,password=pwd)
        if user:
            auth.login(request,user)  # request.user
            return redirect("/index/")


    return render(request,"login.html")


from .models import *
import datetime
def index(request):
    date=datetime.datetime.now().date()
    book_date=request.GET.get("book_date",date)
    print("book_date",book_date)

    time_choices=Book.time_choices
    room_list=Room.objects.all()
    book_list=Book.objects.filter(date=book_date)
    print("time_choices",time_choices)


    htmls=""
    for room in room_list:
        htmls+="<tr><td>{}({})</td>".format(room.caption,room.num)

        for time_choice in time_choices:
            book=None
            flag=False
            for book in book_list:
                if book.room.pk==room.pk and book.time_id==time_choice[0]:
                    #意味这个单元格已被预定
                    flag=True
                    break

            if flag:
                if request.user.pk==book.user.pk:
                     htmls += "<td class='active item'  room_id={} time_id={}>{}</td>".format(room.pk, time_choice[0],book.user.username)
                else:
                     htmls += "<td class='another_active item'  room_id={} time_id={}>{}</td>".format(room.pk, time_choice[0],
                                                                                        book.user.username)
            else:
                 htmls+="<td room_id={} time_id={} class='item'></td>".format(room.pk,time_choice[0])

        htmls+="</tr>"




    # print(htmls)


    return render(request,"index.html",locals())

import json


def book(request):

    # print("request.POST",request.POST)

    post_data=json.loads(request.POST.get("post_data")) # {"ADD":{"1":["5"],"2":["5","6"]},"DEL":{"3":["9","10"]}}
    # print("post_data", post_data)
    choose_date=request.POST.get("choose_date")

    res={"state":True,"msg":None}
    try:
        # 添加预定
        #post_data["ADD"] : {"1":["5"],"2":["5","6"]}

        book_list=[]
        for room_id,time_id_list in post_data["ADD"].items():

            for time_id in time_id_list:
                book_obj=Book(user=request.user,room_id=room_id,time_id=time_id,date=choose_date)
                book_list.append(book_obj)

        Book.objects.bulk_create(book_list)


        # 删除预定
        from django.db.models import Q
        # post_data["DEL"]: {"2":["2","3"]}

        # print("post_data['DEL']:", post_data["DEL"].items())
        remove_book = Q()
        for room_id,time_id_list in post_data["DEL"].items():

            temp = Q()
            for time_id in time_id_list:
                temp.children.append(("room_id",room_id))
                temp.children.append(("time_id",time_id))
                temp.children.append(("user_id",request.user.pk))
                temp.children.append(("date",choose_date))
                remove_book.add(temp,"OR")
        if remove_book:
             Book.objects.filter(remove_book).delete()



    except Exception as e:
        res["state"]=False
        res["msg"]=str(e)

    return HttpResponse(json.dumps(res))
