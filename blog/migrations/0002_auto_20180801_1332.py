# Generated by Django 2.0.6 on 2018-08-01 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='comment_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='article',
            name='down_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='article',
            name='up_count',
            field=models.IntegerField(default=0),
        ),
    ]
