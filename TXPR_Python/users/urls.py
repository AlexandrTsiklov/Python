from django.urls import path
from users.views import *


urlpatterns = [
    path('registration', Registration, name='registration'),
    path('authorization', Login, name='authorization'),
    path('logout', Logout, name='logout'),


    path('home', home, name='home'),

    path('make_order', make_order, name='make_order'),
    path('save_get_order', save_get_order, name='save_get_order'),
    path('save_delivery_order', save_delivery_order, name='save_delivery_order'),
    path('get_all_my_orders', get_all_my_orders, name='get_all_my_orders'),
    path('find_deliverer', find_deliverer, name='find_deliverer'),
    path('find_customer', find_customer, name='find_customer'),

    path('send_otklik_na_zakaz', send_otklik_na_zakaz, name='send_otklik_na_zakaz'),
    path('send_otklik_na_delivery', send_otklik_na_delivery, name='send_otklik_na_delivery'),

    path('get_all_my_otkliks', get_all_my_otkliks, name='get_all_my_otkliks'),

    path('get_people_who_responsed_this_order', get_people_who_responsed_this_order, name='get_people_who_responsed_this_order'),

    path('action_with_otklik', action_with_otklik, name='action_with_otklik'),
    path('was_seen_true', was_seen_true, name='was_seen_true'),

    path('wait_to_get', wait_to_get, name='wait_to_get'),
    path('confirm_getting', confirm_getting, name='confirm_getting'),
    path('delete_order_i_left', delete_order_i_left, name='delete_order_i_left'),
    path('cancel_otklik', cancel_otklik, name='cancel_otklik'),

    path('making_order', making_order, name='making_order'),

    path('show_chat', show_chat, name='show_chat'),
    path('send_message', send_message, name='send_message'),

    path('show_history', show_history, name='show_history'),
    path('save_avatar', save_avatar, name='save_avatar'),
    path('get_target_user_media', get_target_user_media, name='get_target_user_media'),
    path('get_target_user_media_MO', get_target_user_media_MO, name='get_target_user_media_MO'),

    path('publish_otziv', publish_otziv, name='publish_otziv'),
    path('get_otzivi', get_otzivi, name='get_otzivi'),
    path('chat_real_time', chat_real_time, name='chat_real_time')
]