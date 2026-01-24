# Generated migration for adding payment tracking fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aso', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Payment'),
                    ('failed', 'Payment Failed'),
                    ('confirmed', 'Payment Confirmed'),
                    ('cancelled', 'Cancelled'),
                ],
                db_index=True,
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_reference',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                help_text='paystack, flutterwave, monnify',
            ),
        ),
    ]
