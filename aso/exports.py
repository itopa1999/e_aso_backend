from import_export import fields, resources
from .models import Product, ProductColor, ProductSize, ProductDetail, Category
from import_export.widgets import ManyToManyWidget


class ProductResource(resources.ModelResource):
    id = fields.Field(attribute='id', column_name='id', default=None)
    
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ManyToManyWidget(Category, field='name', separator=',')
    )

    sizes = fields.Field(column_name='sizes')
    colors = fields.Field(column_name='colors')
    details = fields.Field(column_name='details')

    class Meta:
        model = Product
        import_id_fields = ['id']
        fields = (
            'title', 'description', 'rating', 'original_price', 'discount_percent',
            'category', 'sizes', 'colors', 'details'
        )

    def after_save_instance(self, instance, using_transactions, dry_run):
        if not instance.pk:
            instance.display_product = False

        # Sizes (expecting a list like ["S", "M", "L"])
        sizes_list = self.fields['sizes'].clean(instance)
        if isinstance(sizes_list, list):
            for size in sizes_list:
                ProductSize.objects.get_or_create(product=instance, size_label=size.strip())

        # Colors (expecting a list of dicts like [{"name": "White", "hex": "#FFF"}])
        colors_list = self.fields['colors'].clean(instance)
        if isinstance(colors_list, list):
            for color in colors_list:
                try:
                    name = color.get("name")
                    hex_code = color.get("hex")
                    if name and hex_code:
                        ProductColor.objects.get_or_create(
                            product=instance,
                            color_name=name.strip(),
                            hex_code=hex_code.strip()
                        )
                except Exception:
                    continue

        # Details (expecting a list of dicts like [{"tab": "Fabric", "content": "Cotton"}])
        details_list = self.fields['details'].clean(instance)
        if isinstance(details_list, list):
            for detail in details_list:
                try:
                    tab = detail.get("tab")
                    content = detail.get("content")
                    if tab and content:
                        ProductDetail.objects.get_or_create(
                            product=instance,
                            tab=tab.strip(),
                            title=tab.strip().capitalize(),
                            content=content.strip()
                        )
                except Exception:
                    continue
