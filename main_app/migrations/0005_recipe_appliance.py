# Generated by Django 4.2.7 on 2023-11-28 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_merge_0003_recipe_bookmarks_0003_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='appliance',
            field=models.CharField(choices=[('Oven', 'Oven'), ('Stove', 'Stove'), ('Instant Pot', 'Instant Pot')], max_length=20, null=True),
        ),
    ]