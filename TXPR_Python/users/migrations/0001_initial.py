# Generated by Django 4.0.5 on 2022-06-04 13:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('person_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(max_length=100, unique=True, verbose_name='Имя пользователя')),
                ('password', models.CharField(max_length=100, verbose_name='Пароль')),
                ('photo', models.ImageField(default='photos/default/default.jpg', upload_to='photos', verbose_name='Аватар')),
                ('rating', models.FloatField(default=0.0, verbose_name='Рейтинг')),
                ('otziv_count', models.IntegerField(default=0, verbose_name='Количество отзывов')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person_one', models.IntegerField(verbose_name='Одна сторона')),
                ('person_two', models.IntegerField(verbose_name='Вторая сторона')),
                ('for_whom', models.IntegerField(null=True, verbose_name='Кому надо показать')),
                ('message', models.CharField(max_length=1000000, verbose_name='Сообщение')),
                ('time', models.DateTimeField(auto_now=True)),
                ('was_seen', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('order_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('from_city', models.CharField(max_length=255, verbose_name='Откуда')),
                ('to_city', models.CharField(max_length=255, verbose_name='Куда')),
                ('time', models.IntegerField(choices=[(12, 12), (14, 14), (16, 16), (18, 18), (20, 20)], verbose_name='Ко скольки')),
                ('goods', models.CharField(default='---', max_length=255, verbose_name='Что')),
                ('price', models.CharField(default='---', max_length=50, null=True, verbose_name='Цена')),
                ('comment', models.CharField(default='---', max_length=255, null=True, verbose_name='Комментарий')),
                ('get_or_deliver', models.CharField(blank=True, max_length=255, verbose_name='Тип')),
                ('who_took', models.IntegerField(null=True, verbose_name='Кто взял заказ')),
                ('who_wait', models.IntegerField(null=True, verbose_name='Кто ожидает')),
                ('time_complete', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Responses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField(verbose_name='ID заявки')),
                ('whose_order', models.IntegerField(verbose_name='Чей заказ')),
                ('who_replied', models.IntegerField(verbose_name='Кто откликнулся')),
                ('get_or_deliver', models.CharField(blank=True, max_length=255, verbose_name='Доставить или получить')),
                ('was_seen', models.BooleanField(default=False, verbose_name='Было прочитано')),
                ('sopr_message', models.CharField(blank=True, max_length=10000, null=True, verbose_name='Сопроводительное письмо')),
            ],
        ),
        migrations.CreateModel(
            name='Otzivi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otziv', models.CharField(max_length=10000, verbose_name='Отзыв')),
                ('who_left_id', models.IntegerField(verbose_name='Кто оставил ID')),
                ('who_left_username', models.CharField(max_length=1000, verbose_name='Кто оставил - имя')),
                ('for_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('from_city', models.CharField(choices=[('Москва', 'Москва'), ('Кольчугино', 'Кольчугино'), ('Владимир', 'Владимир'), ('Санкт-Питербург', 'Санкт-Питербург'), ('Нижний Новгород', 'Нижний Новгород')], max_length=255, verbose_name='Откуда')),
                ('to_city', models.CharField(choices=[('Москва', 'Москва'), ('Кольчугино', 'Кольчугино'), ('Владимир', 'Владимир'), ('Санкт-Питербург', 'Санкт-Питербург'), ('Нижний Новгород', 'Нижний Новгород')], max_length=255, verbose_name='Куда')),
                ('time', models.IntegerField(choices=[(12, 12), (14, 14), (16, 16), (18, 18), (20, 20)], verbose_name='Ко скольки')),
                ('goods', models.CharField(default='---', max_length=255, verbose_name='Что')),
                ('price', models.CharField(default='---', max_length=50, null=True, verbose_name='Цена')),
                ('comment', models.CharField(default='---', max_length=255, null=True, verbose_name='Комментарий')),
                ('get_or_deliver', models.CharField(blank=True, max_length=255, verbose_name='Тип')),
                ('was_taken', models.BooleanField(default=False, verbose_name='На исполнении')),
                ('who_took', models.IntegerField(null=True, verbose_name='Кто взял заказ')),
                ('who_wait', models.IntegerField(null=True, verbose_name='Кто ожидает')),
                ('whose_order', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='ID человека')),
            ],
        ),
    ]
