from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0002_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='order',
            name='customer_name',
            field=models.CharField(blank=True, max_length=255, default=''),
        ),
    ]
