from django.contrib.auth import login, authenticate
from django.contrib.auth.views import logout_then_login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from users.forms import *
from users.models import *


#---------------Внешний вид предупреждений в формах---------------

from django.forms.utils import ErrorList


class MY_ERRORS(ErrorList):

    def __str__(self):
         return self.as_divs()

    def as_divs(self):
        if not self: return ''
        return ''


#---------------Регистрация и авторизация---------------

def Registration(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST["password1"])
            user.save()

            cd = form.cleaned_data
            user_auth = authenticate(username=cd['username'], password=cd['password1'])
            login(request, user_auth)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'users/registration.html', {'form': form})


def Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user.is_authenticated:
                login(request, user)
                return redirect('home')
            else:
                return redirect('authorization')
    else:
        form = LoginForm()
    return render(request, 'users/authorization.html', {'form': form})


def Logout(req):
    login_url = reverse_lazy('authorization')
    return logout_then_login(req, login_url)


def save_avatar(request):
    user_id = request.user.person_id

    try:
        avatar = request.FILES['photo']
    except:
        return HttpResponse('<h1>Не могу достать из request</h1>')

    target_user = MyUser.objects.get(person_id=user_id)
    target_user.photo = avatar

    try:
        target_user.save()
    except:
        return HttpResponse('<h1>Не могу сохранить в БД</h1>')

    return redirect('home')


def get_target_user_media(request):
    target_user = request.GET['target_user']
    target_user_obj = MyUser.objects.get(person_id=target_user)

    photo_and_rating_dict = {
        'username': target_user_obj.username,
        'photo': target_user_obj.photo.url,
        'rating': target_user_obj.rating
    }
    return JsonResponse(photo_and_rating_dict)


def get_target_user_media_MO(request):
    target_user = request.GET['target_user']
    target_user_obj = MyUser.objects.get(username=target_user)

    dict_user_info = {
        'photo': target_user_obj.photo.url,
        'rating': target_user_obj.rating
    }
    return JsonResponse(dict_user_info)


#-------------------------Домашняя страница-----------------------

def home(request):
    load_avatar_form = LoadAvatar

    if request.user.is_anonymous:
        return redirect('authorization')

    if request.user.is_authenticated:
        user = MyUser.objects.get(person_id=request.user.person_id)
        print(round(user.rating, 3))
        return render(request, 'users/home.html', {'username': user.username,
                                                   'rating': user.rating,
                                                   'photo': user.photo,
                                                   'load_avatar_form': load_avatar_form})
    else:
        return redirect('authorization')


def get_all_my_otkliks(request):
    user_id = request.user.person_id

    # Получаем список всех моих откликов из БД с откликами
    all_my_otkliks_list = list(Responses.objects.filter(who_replied=user_id))

    # Создаём список из id заявок, на которые я откликнулся
    offers_id_list = []
    for i in range(len(all_my_otkliks_list)):
        offers_id_list.append(all_my_otkliks_list[i].order_id)

    # Достаём из БД с заявками толко те, которые есть в списке
    all_the_orders_i_responsed = list(Orders.objects.filter(order_id__in=offers_id_list).exclude(was_taken=True))

    dict_with_all_responsed_orders= {}

    for i in range(len(all_the_orders_i_responsed)):
        # Достаём имя юзера по известному id заявки
        whose_order = MyUser.objects.get(orders__order_id=all_the_orders_i_responsed[i].order_id)

        dict_with_all_responsed_orders['order_i_replied_' + str(i)] = [
            all_the_orders_i_responsed[i].order_id,
            whose_order.username,
            all_the_orders_i_responsed[i].from_city,
            all_the_orders_i_responsed[i].to_city,
            all_the_orders_i_responsed[i].time,
            all_the_orders_i_responsed[i].goods,
            all_the_orders_i_responsed[i].price,
            all_the_orders_i_responsed[i].comment,
            all_the_orders_i_responsed[i].get_or_deliver,
            whose_order.person_id]

    return JsonResponse(dict_with_all_responsed_orders)


def get_all_my_orders(request):
    if request.method == 'GET':
        # Все мои оставленные заявки из БД заказов
        all_my_orders = list(Orders.objects.filter(whose_order=request.user.person_id, was_taken=False))
        # Все новые отклики на мои заказы из БД откликов
        list_all_otkliks = list(Responses.objects.filter(whose_order=request.user.person_id))
        list_new_otkliks = list(Responses.objects.filter(whose_order=request.user.person_id, was_seen=False))
        count_new_otkliks = len(list_new_otkliks)

        # В этом списке все id заказов, получивших отклики
        lst_id_orders_that_got_otklik = []
        for otklik in list_new_otkliks:
            lst_id_orders_that_got_otklik.append(otklik.order_id)
        set_id_orders_that_got_otklik = set(lst_id_orders_that_got_otklik)

        # Словарь: id_заказа - количество новых откликов на него
        dict_order_id_otklik_count = {}
        for order_id in set_id_orders_that_got_otklik:
            dict_order_id_otklik_count[order_id] = lst_id_orders_that_got_otklik.count(order_id)

        dict_with_all_my_otkliks = {}
        for otklik in list_all_otkliks:
            who_replied_username = MyUser.objects.get(person_id=otklik.who_replied).username
            dict_with_all_my_otkliks['otklik_' + str(otklik.id)] = [
                otklik.order_id,
                who_replied_username
            ]

        # Словарь всез моих оставленных заказов
        dict_with_all_my_orders = {}
        for i in range(len(all_my_orders)):
            dict_with_all_my_orders['order_' + str(i)] = [
                                 all_my_orders[i].from_city,
                                 all_my_orders[i].to_city,
                                 all_my_orders[i].time,
                                 all_my_orders[i].goods,
                                 all_my_orders[i].price,
                                 all_my_orders[i].order_id,
                                 all_my_orders[i].comment,
                                 all_my_orders[i].get_or_deliver]

        dict_to_send = {
            'dict_with_all_my_offers': dict_with_all_my_orders,
            'dict_order_id_otklik_count': dict_order_id_otklik_count,
            'dict_with_all_my_otkliks': dict_with_all_my_otkliks,
            'count_new_otkliks': count_new_otkliks
        }
        return JsonResponse(dict_to_send)

    return HttpResponse(status=200)


def wait_to_get(request):
    wait_to_get_obj_list = list(Orders.objects.filter(who_wait=request.user.person_id, was_taken=True))

    # Закидываем всё, что мне кто-то доставляет в словарь
    wait_to_get_obj_dict = {}
    for obj in wait_to_get_obj_list:
        who_took = MyUser.objects.get(person_id=obj.who_took).username

        wait_to_get_obj_dict['wait_to_get_order_' + str(obj.order_id)] = [
            obj.order_id,
            obj.from_city,
            obj.to_city,
            obj.time,
            obj.goods,
            obj.price,
            obj.comment,
            obj.get_or_deliver,
            who_took,
            obj.who_wait,
            obj.who_took]

    return JsonResponse(wait_to_get_obj_dict)


def making_order(requst):
    orders_i_making_obj = list(Orders.objects.filter(was_taken=True, who_took=requst.user.person_id))

    dict_with_orders_i_making = {}
    for order in orders_i_making_obj:
        who_wait_username = MyUser.objects.get(person_id=order.who_wait).username

        dict_with_orders_i_making['i_making_' + str(order.order_id)] = [
            order.order_id,
            order.from_city,
            order.to_city,
            order.goods,
            order.time,
            order.price,
            order.comment,
            order.get_or_deliver,
            order.who_took,
            order.who_wait,
            who_wait_username
        ]

    return JsonResponse(dict_with_orders_i_making)


def publish_otziv(request):
    text_otziva = request.GET['text_otziva'],
    left_rating = float(request.GET['left_rating'])
    about_who = request.GET['about_who']
    who_left = request.user.person_id

    clear_text_otziva = list(text_otziva)[0]

    try:
        Otzivi.objects.get(who_left_id=who_left, for_user_id=about_who)
        return HttpResponse('unsuccess')
    except:
        about_who_obj = MyUser.objects.get(person_id=about_who)
        if about_who_obj.rating > 0:
            about_who_obj.rating = round(((about_who_obj.rating * about_who_obj.otziv_count) + left_rating) / (about_who_obj.otziv_count + 1), 2)
        else:
            about_who_obj.rating = round(left_rating, 2)
        about_who_obj.otziv_count += 1

        about_who_obj.save()

        Otzivi.objects.create(
            otziv = clear_text_otziva,
            who_left_id = who_left,
            who_left_username = MyUser.objects.get(person_id=who_left).username,
            for_user_id = about_who
        )
        return HttpResponse('success')


def get_otzivi(request):
    about_who = request.GET['person']
    about_who_id = MyUser.objects.get(username=about_who)
    otzivi_list = list(Otzivi.objects.filter(for_user_id=about_who_id))

    dict_with_otzivi = {}
    for i in range(len(otzivi_list)):
        dict_with_otzivi['otziv_' + str(i)] = [
            otzivi_list[i].who_left_username,
            otzivi_list[i].otziv]

    return JsonResponse(dict_with_otzivi)



# -------------------------Логика заказов-------------------------

def make_order(request):
    if request.user.is_anonymous:
        return redirect('authorization')

    load_avatar_form = LoadAvatar

    if request.user.is_authenticated:
        user = MyUser.objects.get(person_id=request.user.person_id)
        return render(request, 'users/make_order.html', {'username': user.username,
                                                         'rating': user.rating,
                                                         'photo': user.photo,
                                                         'load_avatar_form': load_avatar_form})
    else:
        return redirect('authorization')


def save_get_order(request):
    if request.method == 'GET':
        order_info_list = list(request.GET.values())

        from_f = order_info_list[0]
        to_f = order_info_list[1]
        time_f = order_info_list[2]
        goods_f = order_info_list[3]
        price_f = order_info_list[4]
        comment_f = order_info_list[5]
        get_or_deliver_f = order_info_list[6]

        offer = Orders(
            from_city = from_f,
            to_city = to_f,
            time = time_f,
            goods = goods_f,
            price = price_f,
            comment = comment_f,
            get_or_deliver = get_or_deliver_f
        )
        offer.save()

        # связываем заявку и человека, через доп.таблицу
        person = MyUser.objects.get(person_id=request.user.person_id)
        offer.whose_order.add(person)
    else:
        pass
    return HttpResponse(status=200)


def save_delivery_order(request):
    if request.method == 'GET':
        order_info_list = list(request.GET.values())

        from_f = order_info_list[0]
        to_f = order_info_list[1]
        time_f = order_info_list[2]
        comment_f = order_info_list[3]
        get_or_deliver_f = order_info_list[4]

        offer = Orders(
            from_city = from_f,
            to_city = to_f,
            time = time_f,
            goods = '---',
            comment = comment_f,
            get_or_deliver = get_or_deliver_f
        )
        offer.save()

        # связываем заявку и человека, через доп.таблицу
        person = MyUser.objects.get(person_id=request.user.person_id)
        offer.whose_order.add(person)
    else:
        pass
    return HttpResponse(status=200)


def find_deliverer(request):
    id_user_who_searching = request.user.person_id
    orders_that_user_already_replied = list(Responses.objects.filter(who_replied=id_user_who_searching, get_or_deliver='get'))

    # ------------список с id заказов, на которые юзер уже откликнулся----------
    id_offers_that_user_already_replied = []
    for order in orders_that_user_already_replied:
        id_offers_that_user_already_replied.append(order.order_id)
    # --------------------------------------------------------------------------

    # Параметры из формы для поиска в БД
    search_params = list(request.GET.values())

    # Пока фильтрация только по конечному городу
    final_city = search_params[1]

    # Получаем заказы, на которые юзер ещё не откликнулся                                     # Это вместо or
    delivery_offers =list(Orders.objects.filter(to_city=final_city, get_or_deliver='deliver', was_taken=False).exclude(Q(order_id__in=id_offers_that_user_already_replied) | Q(whose_order=id_user_who_searching)))
    dict_founded_delivery_offers = {}


    for i in range(len(delivery_offers)):
        # Достаём имя юзера по известному id заявки
        whose_order = MyUser.objects.get(orders__order_id=delivery_offers[i].order_id).username

        dict_founded_delivery_offers['delivery_offer_' + str(i)] = [
            whose_order,
            delivery_offers[i].from_city,
            delivery_offers[i].to_city,
            delivery_offers[i].time,
            delivery_offers[i].order_id,
            delivery_offers[i].comment,
            delivery_offers[i].get_or_deliver]

    return JsonResponse(dict_founded_delivery_offers)


def find_customer(request):
    id_user_who_searching = request.user.person_id
    orders_that_user_already_replied = list(Responses.objects.filter(who_replied=id_user_who_searching, get_or_deliver='deliver'))

    # ------------список с id заказов, на которые юзер уже откликнулся----------
    id_offers_that_user_already_replied = []
    for order in orders_that_user_already_replied:
        id_offers_that_user_already_replied.append(order.order_id)
    # --------------------------------------------------------------------------

    # Параметры из формы для поиска в БД
    search_params = list(request.GET.values())

    # Пока фильтрация только по конечному городу
    final_city = search_params[1]

    # Получаем заказы, на которые юзер ещё не откликнулся                                                                                     # Это вместо or
    customer_orders =list(Orders.objects.filter(to_city=final_city, get_or_deliver='get').exclude(Q(order_id__in=id_offers_that_user_already_replied) | Q(whose_order=id_user_who_searching)))
    dict_founded_customer_orders = {}

    for i in range(len(customer_orders)):
        # Достаём имя юзера по известному id заявки
        whose_order = MyUser.objects.get(orders__order_id=customer_orders[i].order_id).username

        dict_founded_customer_orders['customer_order_' + str(i)] = [
            whose_order,
            customer_orders[i].from_city,
            customer_orders[i].to_city,
            customer_orders[i].time,
            customer_orders[i].goods,
            customer_orders[i].price,
            customer_orders[i].order_id,
            customer_orders[i].comment,
            customer_orders[i].get_or_deliver]

    return JsonResponse(dict_founded_customer_orders)


def delete_order_i_left(request):
    order_id = request.GET['order_id']
    target_order = Orders.objects.get(order_id=order_id)
    target_order.delete()
    return HttpResponse(status=200)



# -------------------------Логика откликов-------------------------

def send_otklik_na_zakaz(request):
    id_order_that_got_otklik = list(request.GET.values())[0]
    id_user_that_made_otklik = request.user.person_id
    id_user_whose_order = MyUser.objects.get(orders__order_id=id_order_that_got_otklik).person_id
    sopr_message = request.GET['sopr_message']

    responce = Responses(
        order_id = id_order_that_got_otklik,
        whose_order = id_user_whose_order,
        who_replied = id_user_that_made_otklik,
        get_or_deliver = 'deliver',
        was_seen = False,
        sopr_message = sopr_message
    )
    responce.save()

    return HttpResponse(status=200)


def cancel_otklik(request):
    order_id = request.GET['order_id']
    user_id = request.user.person_id

    target_otklik = Responses.objects.get(order_id=order_id, who_replied=user_id)
    target_otklik.delete()

    return HttpResponse(status=200)


def send_otklik_na_delivery(request):
    id_order_that_got_otklik = list(request.GET.values())[0]
    id_user_that_made_otklik = request.user.person_id
    id_user_whose_order = MyUser.objects.get(orders__order_id=id_order_that_got_otklik).person_id
    sopr_message = request.GET['sopr_message']

    responce = Responses(
        order_id=id_order_that_got_otklik,
        whose_order=id_user_whose_order,
        who_replied=id_user_that_made_otklik,
        get_or_deliver='get',
        was_seen=False,
        sopr_message=sopr_message,
    )
    responce.save()

    return HttpResponse(status=200)


def get_people_who_responsed_this_order(request):
    target_id_order = list(request.GET.values())[0]

    # Список id всех людей, откликнувшихся на конкретный заказ
    objects_people_who_responsed_it_all = list(Responses.objects.filter(order_id=target_id_order))
    list_people_id = []
    for obj in objects_people_who_responsed_it_all:
        list_people_id.append(obj.who_replied)

    # Список id людей, отклики которых ещё не были просмотрены
    objects_people_who_responsed_it_new = list(Responses.objects.filter(order_id=target_id_order, was_seen=False))
    list_new_people_id = []
    for obj in objects_people_who_responsed_it_new:
        list_new_people_id.append(obj.who_replied)

    # Достаём людей из БД в соответствии с этим списком
    people_who_responsed_it_all = list(MyUser.objects.filter(person_id__in=list_people_id))

    # Закидываем человека с его данными в словарь
    dict_people_who_responsed_it_all = {}

    for person_obj in people_who_responsed_it_all:
        was_seen = not person_obj.person_id in list_new_people_id
        sopr_message = Responses.objects.get(order_id=target_id_order, who_replied=person_obj.person_id).sopr_message

        dict_people_who_responsed_it_all['person_' + str(person_obj.person_id)] = [
            person_obj.person_id,
            person_obj.username,
            was_seen,
            person_obj.photo.url,
            person_obj.rating,
            sopr_message
        ]

    return JsonResponse(dict_people_who_responsed_it_all)


def action_with_otklik(request):
    order_id = request.GET['order_id'][0]
    action = request.GET['action']
    who_replied_id = request.GET['who_replied_id']
    get_or_deliver = request.GET['get_or_deliver']

    result = 'nothing'

    # Если я в поиске откликнулся на заявку доставки
    if get_or_deliver == 'deliver':
        if action == 'confirm':
            target_order = Orders.objects.get(order_id=order_id)
            target_order.was_taken = True
            target_order.who_took = request.user.person_id
            target_order.who_wait = who_replied_id
            target_order.save()
            result = 'was_confirmed'
        elif action == 'decline':
            Responses.objects.get(order_id=order_id, who_replied=who_replied_id).delete()
            result = 'was_deleted'
    # Если я в поиске откликнулся на заявку заказа
    else:
        if action == 'confirm':
            target_order = Orders.objects.get(order_id=order_id)
            target_order.was_taken = True
            target_order.who_took = who_replied_id
            target_order.who_wait = request.user.person_id
            target_order.save()
            result = 'was_confirmed'
        elif action == 'decline':
            Responses.objects.get(order_id=order_id, who_replied=who_replied_id).delete()
            result = 'was_deleted'

    return HttpResponse(result)


def was_seen_true(request):
    order_id = request.GET['order_id']
    who_replied_id = request.GET['who_replied_id']

    otklik_that_was_read = Responses.objects.get(order_id=order_id, who_replied=who_replied_id)
    otklik_that_was_read.was_seen = True
    otklik_that_was_read.save()

    return HttpResponse(status=200)


def confirm_getting(request):
    order_id = request.GET['order_id']
    target_order = Orders.objects.get(order_id=order_id)

    History.objects.create(
        order_id = order_id,
        from_city = target_order.from_city,
        to_city = target_order.to_city,
        time = target_order.time,
        goods = target_order.goods,
        price = target_order.price,
        comment = target_order.comment,
        get_or_deliver = target_order.get_or_deliver,
        who_took = target_order.who_took,
        who_wait = target_order.who_wait
    )

    target_order.delete()
    return HttpResponse(status=200)



# -----------------------------Чат-----------------------------

def show_chat(request):
    he = request.GET['chat_with']
    me = request.user.person_id

    all_chat_list = list(Chat.objects.filter(Q(person_one=me, person_two=he) | Q(person_one=he, person_two=me)).order_by('time'))


    all_chat_dict = {}
    for i in range(len(all_chat_list)):

        if all_chat_list[i].was_seen is False:
            all_chat_list[i].was_seen = True
            all_chat_list[i].save()

        all_chat_dict['message_' + str(all_chat_list[i].id)] = [
            all_chat_list[i].person_one,
            all_chat_list[i].person_two,
            all_chat_list[i].for_whom,
            all_chat_list[i].message,
            me
        ]

    return JsonResponse(all_chat_dict)


def send_message(request):
    he = request.GET['chat_with']
    me = request.user.person_id
    message = request.GET['message']

    Chat.objects.create(
        person_one = he,
        person_two = me,
        for_whom = he,
        message = message
    )
    return HttpResponse(status=200)


def chat_real_time(request):
    he = request.GET['chat_with']
    me = request.user.person_id

    all_chat_list = list(Chat.objects.filter((Q(person_one=me, person_two=he) | Q(person_one=he, person_two=me)), for_whom=me, was_seen=False).order_by('time'))

    dict_of_messages = {}
    for i in range(len(all_chat_list)):

        all_chat_list[i].was_seen = True
        all_chat_list[i].save()

        dict_of_messages['message_' + str(all_chat_list[i].id)] = [
            all_chat_list[i].person_one,
            all_chat_list[i].person_two,
            all_chat_list[i].for_whom,
            all_chat_list[i].message,
            me
        ]

    return JsonResponse(dict_of_messages)


# -----------------------------История-----------------------------

def show_history(request):
    user_id = request.user.person_id
    history_objects_list = list(History.objects.filter(Q(who_took=user_id) | Q(who_wait=user_id)).order_by('time_complete'))

    dict_history = {}

    for i in range(len(history_objects_list)):
        who_wait = MyUser.objects.get(person_id=history_objects_list[i].who_wait).username
        who_took = MyUser.objects.get(person_id=history_objects_list[i].who_took).username

        dict_history['order_' + str(history_objects_list[i].order_id)] = [
            history_objects_list[i].order_id,
            history_objects_list[i].from_city,
            history_objects_list[i].to_city,
            history_objects_list[i].time,
            history_objects_list[i].goods,
            history_objects_list[i].price,
            history_objects_list[i].comment,
            history_objects_list[i].get_or_deliver,
            who_took,
            who_wait,
            history_objects_list[i].time_complete
        ]
    return JsonResponse(dict_history)