# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-02 09:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0009_auto_20171109_1010'),
        ('crm', '0004_salerank'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='auth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.User', verbose_name='用户权限'),
        ),
    ]