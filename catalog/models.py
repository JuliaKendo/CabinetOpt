from django.db import models
from contextlib import suppress
from django.core.validators import MinValueValidator
from django.db.models import F, Q, Max
from django.utils import timezone

from clients.models import PriorityDirection, Client


class CollectionGroup(models.Model):
    name = models.CharField('Наименование', max_length=100, db_index=True)

    class Meta:
        verbose_name = 'Группа коллекций'
        verbose_name_plural = 'Группы коллекций'

    def __str__(self):
        return self.name


class Collection(models.Model):
    group = models.ForeignKey(
        CollectionGroup,
        on_delete=models.PROTECT,
        verbose_name='Группа',
        related_name='collections',
        db_index=True,
    )
    name = models.CharField('Наименование', max_length=100, db_index=True)
    discount = models.DecimalField(
        'Скидка',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    identifier_1C = models.CharField(
        'Идентификатор 1С', max_length=50, blank=True, db_index=True
    )

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField('Гендер', max_length=100, db_index=True)

    class Meta:
        verbose_name = 'Гендер'
        verbose_name_plural = 'Гендер'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    
    def apply_filters(self, filters):
        result = self.distinct()
        for key, value in filters.items():
            if key == 'name':
                result = result.filter(name__in=value.split(';'))
            elif key == 'articul':
                result = result.filter(articul__icontains=value)
            elif key == 'unit':
                result = result.filter(unit=value)
            elif key == 'status':
                result = result.filter(status=value)
        return result


class Product(models.Model):
    name = models.CharField('Наименование', max_length=200, db_index=True)
    articul = models.CharField('Артикул', max_length=200, blank=True)
    collection = models.ForeignKey(
        Collection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Коллекция',
        related_name='collection_products',
        db_index=True,
    )
    brand = models.ForeignKey(
        PriorityDirection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Бренд',
        related_name='brand_products'        
    )
    unit = models.CharField(
        'Единица измерения',
        max_length=20,
        default='грамм',
        db_index=True,
        choices=(
            ('796', 'штук'),
            ('163', 'грамм'),
    ))
    available_for_order = models.BooleanField(
        'Доступен для заказа', default=False, db_index=True
    )
    created_at = models.DateTimeField(
        'Дата создания', db_index=True, auto_now_add=True
    )
    product_type = models.CharField(
        'Тип номенклатуры',
        max_length=20,
        default='product',
        db_index=True,
        choices=(
            ('product', 'товар'),
            ('service', 'услуга'),
            ('gift_сertificate', 'подарочный сертификат')
    ))
    metal = models.CharField('Металл', max_length=50, blank=True, db_index=True)
    metal_content = models.CharField('Проба', max_length=30, blank=True, db_index=True)
    metal_finish = models.CharField('Обработка металла', max_length=50, blank=True, db_index=True)
    color = models.CharField('Цвет', max_length=50, blank=True, db_index=True)
    gender = models.ForeignKey(
        Gender,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.SET_NULL,
        verbose_name='Гендер',
        related_name='products_by_gender'        
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        blank=True,
        db_index=True,
        choices=(
            ('novelty', 'NEW!'),
            ('order'  , 'ЗАКАЗ'),
            ('hit'    , 'ХИТ'),
            ('sale'   , 'ВЫГОДНО'),
    ))
    identifier_1C = models.CharField(
        'Идентификатор 1С', max_length=50, blank=True, db_index=True
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'Номенклатура'
        verbose_name_plural = 'Номенклатура'

    def __str__(self):
        return f'{self.articul} {self.name}'.strip()
    
    @property
    def get_images(self):
        product_images = ProductImage.objects.filter(product_id=self.id)
        return [product_image.image.url for product_image in product_images]
    
    @property
    def get_default_size(self):
        '''Функция возвращает строку, как этап перехода на учет размеров в БД в строковом варианте'''
        size_value = 0
        stocks_and_costs = StockAndCost.objects.\
            filter(product_id=self.id).annotate(size_name=F('size__name')).\
            exclude(size__isnull=True).order_by('size')
        with suppress(AttributeError):
            if self.collection.group.name.lower() in ['кольцо', 'кольца', 'колечки', 'колец']:
                size_value = 20
                if self.gender.name == 'Женский':
                    size_value = 17
            if self.collection.group.name.lower() in ['цепь', 'цепи', 'цепочка', 'цепочек']:
                size_value = 50
        
        found_size = Size.objects.get_current_size(size_value)
        if found_size and stocks_and_costs.filter(size=found_size):
            return found_size.name

        product_size = stocks_and_costs.first()
        if product_size:
            return product_size.size_name


class SizeQuerySet(models.QuerySet):

    def get_by_natural_key(self, size_name):
        return self.get(name=size_name)

    def get_current_size(self, size):
        return self.filter(size_from__lte=size, size_to__gte=size).first()


class Size(models.Model):
    name = models.CharField('Размер', max_length=20, db_index=True, blank=True)
    size_from = models.FloatField(
        'Размер от',
        default=0.0,
        validators=[MinValueValidator(0)]
    )
    size_to = models.FloatField(
        'Размер до',
        default=0.0,
        validators=[MinValueValidator(0)]
    )

    objects = SizeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'
        unique_together = ('size_from', 'size_to')

    def __str__(self):
        return f'{self.name}'
    
    def natural_key(self):
        return (self.name, self.id,)


class StockAndCostQuerySet(models.QuerySet):
    
    def get_by_natural_key(self, first_name, last_name):
        return self.get(first_name=first_name, last_name=last_name)

    def available_stocks_and_costs(self, products_ids, **kwargs):
        clients = kwargs.get('clients', Client.objects.none())
        products = Product.objects.filter(pk__in = products_ids)
        stocks_and_costs = self.filter(product_id__in = products_ids)
        prices = Price.objects.available_prices(products_ids)
        discount_prices = Price.objects.none()
        with suppress(PriceType.DoesNotExist):
            discount_prices = Price.objects.available_prices(
                products_ids, PriceType.objects.get(name='Выгода')
            )
        with suppress(PriceType.DoesNotExist):
            client_prices = Price.objects.available_prices(
                products_ids, PriceType.objects.get(client = clients.get())
            )
            prices = prices.exclude(
                product_id__in = client_prices.values_list('product_id', flat=True)
            ) | client_prices
    
        collections = products.annotate(
            collection_name=F('collection__name'),
            collection_group=F('collection__group__name')
        ).values('id', 'collection_name', 'collection_group')
        
        if kwargs.get('size', ''):
            stocks_and_costs = stocks_and_costs.filter(
                size_id__in=Size.objects.filter(
                    name=kwargs['size']
                ).values_list('pk', flat=True)
            )

        return collections, products, stocks_and_costs, prices, discount_prices

    def default_stocks_and_costs(self, products_ids, **kwargs):
        result = StockAndCost.objects.none()

        products = Product.objects.filter(pk__in = products_ids)
        for product in products:
            default_size = product.get_default_size
            if kwargs.get('size', ''):
                default_size = kwargs['size']
            if default_size:
                result = result | self.filter(
                    product = product, size_id__in = Size.objects.filter(name=default_size).\
                        values_list('pk', flat=True)
                )

        return result


class StockAndCost(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Номенклатура',
        related_name='stocks_and_costs'
    )
    weight = models.FloatField(
        'Вес', default=0, validators=[MinValueValidator(0)]
    )
    size = models.ForeignKey(
        Size,
        null=True,
        blank = True,
        on_delete=models.SET_NULL,
        verbose_name='Размер',
        related_name='sizes'
    )
    stock = models.PositiveIntegerField(
        'Остаток', default=0, validators=[MinValueValidator(0)]
    )    
    cost = models.DecimalField(
        'Максимальная цена за грамм',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    objects = StockAndCostQuerySet.as_manager()

    class Meta:
        verbose_name = 'Наличие и стоимость изделия'
        verbose_name_plural = 'Наличие и стоимость изделий'


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Фото',
        related_name='product_images'
    )
    filename = models.CharField(
        'Имя файла', max_length=100, blank=True, db_index=True
    )
    image = models.ImageField('Фото номенклатуры', upload_to='product_images')

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'


class PriceType(models.Model):
    name = models.CharField('Наименование', max_length=100, db_index=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Клиент',
        related_name='client_prices',
        db_index=True
    )
    class Meta:
        verbose_name = 'Тип цены'
        verbose_name_plural = 'Типы цен'

    def __str__(self):
        return self.name


class PriceQuerySet(models.QuerySet):
    
    def available_prices(self, products_ids, price_type = None):
        with suppress(PriceType.DoesNotExist):
            if not price_type:
                price_type = PriceType.objects.get(name='Базовая')   
            return self.distinct().filter(
                type=price_type,
                product_id__in=products_ids,
                start_at__lte=timezone.now()
            ).filter(
                Q(end_at__isnull=True) | Q(end_at__gte=timezone.now())
            ).annotate(actual_price=Max('price'))


class Price(models.Model):
    type = models.ForeignKey(
        PriceType,
        on_delete=models.CASCADE,
        verbose_name='Тип цены',
        related_name='prices',
        db_index=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Номенклатура',
        related_name='product_prices',
        db_index=True,
    )
    unit = models.CharField(
        'Единица измерения',
        max_length=20,
        default='грамм',
        db_index=True,
        choices=(
            ('796', 'штук'),
            ('163', 'грамм'),
    ))
    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        'Скидка',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    start_at = models.DateTimeField(
        'Дата начала действия', db_index=True, default=timezone.now
    )
    end_at = models.DateTimeField(
        'Дата окончания действия', db_index=True, blank=True,null=True
    )

    objects = PriceQuerySet.as_manager()

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    def __str__(self):
        return f'{self.product} {self.price} руб. ({self.type})'


class PreciousStone(models.Model):
    name = models.CharField('Наименование', max_length=100, db_index=True)
    short_title = models.CharField('Краткое наименование', max_length=10, blank=True)
    identifier_1C = models.CharField(
        'Идентификатор 1С', max_length=50, blank=True, db_index=True
    )

    class Meta:
        verbose_name = 'Камень'
        verbose_name_plural = 'Камни'

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.short_title if self.short_title else self.name


class CutType(models.Model):
    name = models.CharField('Наименование', max_length=100, db_index=True)

    class Meta:
        verbose_name = 'Огранка'
        verbose_name_plural = 'Виды огранки'

    def __str__(self):
        return self.name


class GemSet(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Номенклатура',
        related_name='gem_sets',
        db_index=True
    )
    precious_stone = models.ForeignKey(
        PreciousStone,
        on_delete=models.CASCADE,
        verbose_name='Камни',
        related_name='precious_stones',
        db_index=True
    )
    gem_color = models.CharField('Цвет', max_length=50, blank=True, db_index=True)
    gem_weight = models.FloatField(
        'Вес, кр', default=0, validators=[MinValueValidator(0)]
    )
    order = models.PositiveIntegerField(
        'Порядок', default=1, validators=[MinValueValidator(0)]
    )
    description = models.TextField('Описание', blank=True)
    cut_type = models.ForeignKey(
        CutType,
        on_delete=models.SET_NULL,
        verbose_name='Огранка',
        related_name='cut_types',
        null=True,
        blank=True,
        db_index=True
    )
    comment = models.CharField('Комментарий', max_length=250, blank=True)
    gem_quantity = models.PositiveIntegerField(
        'Количество', default=1, validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Вставка'
        verbose_name_plural = 'Вставки'

    def __str__(self):
        return f'{self.gem_quantity} \
            {repr(self.precious_stone)} \
            {self.cut_type if self.cut_type else ""} - \
            {self.gem_weight} ct'


class ProductsSet(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Номенклатура',
        db_index=True
    )
    accessory = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Комплектующее',
        related_name='set_of_products',
        db_index=True
    )

    class Meta:
        verbose_name = 'Состав'
        verbose_name_plural = 'Состав'

    def __str__(self):
        return f'{self.accessory}'


class SimilarProducts(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Номенклатура',
        db_index=True
    )
    similar_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Аналог',
        related_name='similar_products',
        db_index=True
    )

    class Meta:
        verbose_name = 'Аналог'
        verbose_name_plural = 'Аналоги'

    def __str__(self):
        return f'{self.similar_product}'
