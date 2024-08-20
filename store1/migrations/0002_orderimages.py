# Generated by Django 4.2.14 on 2024-08-01 17:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0015_orderlinediscount'),
        ('catalogue', '0028_productclass_is_customize'),
        ('store1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='order_images')),
                ('user_id', models.IntegerField()),
                ('user_description', models.TextField(max_length=250)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.product')),
            ],
        ),
    ]
