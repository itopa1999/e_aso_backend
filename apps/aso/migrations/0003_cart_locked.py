from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aso', '0002_add_payment_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='locked',
            field=models.BooleanField(default=False, help_text='Cart is locked during payment processing. Prevents user modifications.'),
        ),
        migrations.AddIndex(
            model_name='cart',
            index=models.Index(fields=['locked'], name='aso_cart_locked_idx'),
        ),
    ]
