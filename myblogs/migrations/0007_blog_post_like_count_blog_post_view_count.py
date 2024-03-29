# Generated by Django 5.0.1 on 2024-02-02 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myblogs', '0006_remove_blog_post_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog_post',
            name='like_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='blog_post',
            name='view_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
