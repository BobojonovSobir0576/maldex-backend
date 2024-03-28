# product/management/commands/import_products.py
from django.core.management.base import BaseCommand
from django.apps import apps
import json

class Command(BaseCommand):
    help = 'Import products from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file path containing product data')

    def handle(self, *args, **options):
        Products = apps.get_model('product', 'Products')
        ProductImage = apps.get_model('product', 'ProductImage')
        ProductCategories = apps.get_model('product', 'ProductCategories')  # Ensure this model name matches your actual model

        # Loading JSON data from the specified file
        with open(options['json_file'], 'r', encoding='utf-8') as file:
            data = json.load(file)

            for entry in data:
                # Handling categoryId (adapt this section based on your category handling)
                category_instance = None
                if 'categories' in entry:
                    category_id = entry['categories']
                    category_instance, _ = ProductCategories.objects.get_or_create(id=category_id)

                product, created = Products.objects.update_or_create(
                    id=entry['id'],
                    defaults={
                        'name': entry.get('name'),
                        'full_name': entry.get('full_name'),
                        'brand': entry.get('brand'),
                        'vendor_code': entry.get('article'),
                        'price': entry.get('price'),
                        'price_type': Products.PriceType.RUB,  # Default to RUB; adjust as necessary
                        'categoryId': category_instance,  # Assuming category_instance is correctly handled above
                        'description': entry.get('description'),
                        'attributes': entry.get('attributes', {}),
                        'included_branding': entry.get('included_branding', {}),
                        'discount_price': entry.get('discount_price', 0),
                        # Include additional fields as necessary
                    },
                )

                # Handling product images
                images = entry.get('images', [])
                for img in images:
                    ProductImage.objects.create(
                        productID=product,
                        big=img.get('big', ''),
                        small=img.get('small', ''),
                        superbig=img.get('superbig', ''),
                        thumbnail=img.get('thumbnail', ''),
                    )

        self.stdout.write(self.style.SUCCESS('Successfully imported products from JSON.'))
