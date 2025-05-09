from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investment',
            name='match_attempt_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='queue_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='priority_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='pattern_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='volume_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='risk_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='location_history',
        ),
        migrations.RemoveField(
            model_name='investment',
            name='user_history',
        ),
        migrations.AddField(
            model_name='investment',
            name='maturity_notification_sent',
            field=models.BooleanField(default=False),
        ),
    ] 