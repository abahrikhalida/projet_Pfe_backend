from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='direction_id',
            field=models.CharField(max_length=24, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='departement_id',
            field=models.CharField(max_length=24, null=True, blank=True),
        ),
    ]