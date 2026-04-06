from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_conversation_address_conversation_purchase_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='customer_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='payment_method',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='purchase_state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
