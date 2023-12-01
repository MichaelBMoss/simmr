# Generated by Django 4.2.7 on 2023-11-30 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_alter_recipe_category_alter_review_content_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='content',
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5, null=True),
        ),
    ]
