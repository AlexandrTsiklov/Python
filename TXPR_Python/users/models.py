from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

CITIES = (
('Москва', 'Москва'), ('Кольчугино', 'Кольчугино'), ('Владимир', 'Владимир'), ('Санкт-Питербург', 'Санкт-Питербург'),
('Нижний Новгород', 'Нижний Новгород'))
TIMES = ((12, 12), (14, 14), (16, 16), (18, 18), (20, 20))


# ------------------Модель пользователя и работа с ней------------------

class MyUserManager(BaseUserManager):
    def create_superuser(self, username, password=None):
        if not username:
            raise ValueError('Поле не может быть пустым!')

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    print('Мы в классе MY_USER')
    GENDERS = (
        ('м', 'Мужчина'),
        ('ж', 'Женщина')
    )

    person_id = models.BigAutoField(primary_key=True, unique=True)
    username = models.CharField(verbose_name='Имя пользователя', max_length=100, unique=True)
    password = models.CharField(verbose_name='Пароль', max_length=100, unique=False)

    # fio = models.CharField('ФИО', max_length=255, blank=False, null=True)
    # gender = models.CharField('Пол', max_length=1, choices=GENDERS, blank=False, null=True)
    # date_of_birth = models.DateField('Дата рождения', blank=False, null=True)
    # email = models.EmailField('Почта', max_length=100, blank=False, null=True, unique=True)
    # number = models.IntegerField('Телефон', blank=False, null=True, unique=False)

    photo = models.ImageField('Аватар', upload_to='photos', default='photos/default/default.jpg')
    rating = models.FloatField('Рейтинг', default=0.0)
    otziv_count = models.IntegerField('Количество отзывов', default=0)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('password',)

    is_staff = True

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Otzivi(models.Model):
    for_user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    otziv = models.CharField('Отзыв', max_length=10000)
    who_left_id = models.IntegerField('Кто оставил ID')
    who_left_username = models.CharField('Кто оставил - имя', max_length=1000)


# -----------------------Модели заявки и отклика-------------------------

class Orders(models.Model):
    order_id = models.BigAutoField(primary_key=True, unique=True)
    from_city = models.CharField('Откуда', max_length=255, choices=CITIES)
    to_city = models.CharField('Куда', max_length=255, choices=CITIES)
    time = models.IntegerField('Ко скольки', choices=TIMES)
    goods = models.CharField('Что', max_length=255, default='---')
    price = models.CharField('Цена', max_length=50, null=True, blank=False, default='---')
    comment = models.CharField('Комментарий', max_length=255, null=True, blank=False, default='---')
    get_or_deliver = models.CharField('Тип', max_length=255, null=False, blank=True)
    was_taken = models.BooleanField('На исполнении', default=False)
    who_took = models.IntegerField('Кто взял заказ', null=True)
    who_wait = models.IntegerField('Кто ожидает', null=True)

    whose_order = models.ManyToManyField('MyUser', verbose_name='ID человека')


class Responses(models.Model):
    order_id = models.IntegerField('ID заявки')
    whose_order = models.IntegerField('Чей заказ')
    who_replied = models.IntegerField('Кто откликнулся')
    get_or_deliver = models.CharField('Доставить или получить', max_length=255, null=False, blank=True)
    was_seen = models.BooleanField('Было прочитано', default=False)
    sopr_message = models.CharField('Сопроводительное письмо', max_length=10000, null=True, blank=True)


# ------------------------Модели истории и чата--------------------------

class Chat(models.Model):
    person_one = models.IntegerField('Одна сторона')
    person_two = models.IntegerField('Вторая сторона')
    for_whom = models.IntegerField('Кому надо показать', null=True)
    message = models.CharField('Сообщение', max_length=1000000)
    time = models.DateTimeField(auto_now=True)
    was_seen = models.BooleanField(default=False)


class History(models.Model):
    order_id = models.BigAutoField(primary_key=True, unique=True)
    from_city = models.CharField('Откуда', max_length=255)
    to_city = models.CharField('Куда', max_length=255)
    time = models.IntegerField('Ко скольки', choices=TIMES)
    goods = models.CharField('Что', max_length=255, default='---')
    price = models.CharField('Цена', max_length=50, null=True, blank=False, default='---')
    comment = models.CharField('Комментарий', max_length=255, null=True, blank=False, default='---')
    get_or_deliver = models.CharField('Тип', max_length=255, null=False, blank=True)
    who_took = models.IntegerField('Кто взял заказ', null=True)
    who_wait = models.IntegerField('Кто ожидает', null=True)
    time_complete = models.DateTimeField(auto_now=True)
