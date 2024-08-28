# Generated by Django 4.2.14 on 2024-08-28 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0011_contactvendor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=200, verbose_name='Payment ID')),
                ('order_id', models.CharField(max_length=200, verbose_name='Order ID')),
                ('signature', models.CharField(blank=True, max_length=500, null=True, verbose_name='Signature')),
                ('amount', models.IntegerField(verbose_name='Amount')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
