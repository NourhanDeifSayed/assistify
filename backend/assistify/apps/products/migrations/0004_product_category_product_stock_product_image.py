from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_related_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
