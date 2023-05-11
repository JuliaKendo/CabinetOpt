import io
import json
import base64
from contextlib import suppress
from django.db import transaction
from django.core.files.images import ImageFile

from .models import (
    Product,
    ProductImage,
    Collection,
    PriorityDirection,
)


def run_uploading_products(uploading_products):
    errors = []
    for item in uploading_products:
        try:
            with transaction.atomic():
                identifier_1C = item['nomenclature']['Идентификатор']
                Product.objects.update_or_create(
                    identifier_1C=identifier_1C,
                    defaults = {
                        'name': item['nomenclature']['Наименование'],
                        'articul': item['articul'],
                        'collection': update_or_create_collection(item['collection']),
                        'brand': update_or_create_brand(item['brand']),
                        'unit': item['unit'],
                        'price_per_gr': item['price_per_gr'],
                        'weight': item['weight'],
                        'size': item['size'],
                        'stock': item['stock'],
                        'available_for_order': True,
                        'product_type': item['product_type'],
                        'identifier_1C':identifier_1C
                })

        except ValueError as error:
            transaction.rollback()
            errors.append(item | {"error": str(error)})
            continue
        
        finally:
            if transaction.get_autocommit():
                transaction.commit()
    
    return json.dumps(errors)


def update_or_create_brand(brand):
    if not brand:
        return

    identifier_1C = brand['Идентификатор']
    if identifier_1C == '00000000-0000-0000-0000-000000000000':
        return
    
    if brand['Удален']:
        with suppress(PriorityDirection.DoesNotExist):
            found_collecion = PriorityDirection.objects.get(identifier_1C=identifier_1C)
            found_collecion.delete()
        return

    brand_obj, _ = PriorityDirection.objects.update_or_create(
        identifier_1C=identifier_1C,
        defaults={
            'name': brand['Наименование'],
            'identifier_1C': identifier_1C
    })
    return brand_obj


def update_or_create_collection(collection):
    if not collection:
        return

    identifier_1C = collection['Идентификатор']
    if identifier_1C == '00000000-0000-0000-0000-000000000000':
        return
    
    if collection['Удален']:
        with suppress(Collection.DoesNotExist):
            found_collecion = Collection.objects.get(identifier_1C=identifier_1C)
            found_collecion.delete()
        return
    
    collection_obj, _ = Collection.objects.update_or_create(
        identifier_1C=identifier_1C,
        defaults={
            'name': collection['Наименование'],
            'identifier_1C': identifier_1C
    })

    return collection_obj


def run_uploading_images(uploading_images):
    for item in uploading_images:
        with transaction.atomic():
            identifier_1C = item['nomenclature']['Идентификатор']
            image_bytes = base64.b64decode(item['image'])
            image = ImageFile(io.BytesIO(image_bytes), name=item['filename'])
            
            with suppress(Product.DoesNotExist):
                product = Product.objects.get(identifier_1C=identifier_1C)
                ProductImage.objects.update_or_create(
                    product=product,
                    filename=item['filename'],
                    defaults={
                        'product': product,
                        'filename': item['filename'],
                        'image': image
                })
