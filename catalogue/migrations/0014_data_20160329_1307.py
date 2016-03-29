# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-04 05:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_auto_20160322_1447'),
    ]


    operations = [
        migrations.RunSQL("INSERT INTO catalogue_organization (name, short_name, url, address, city,state_or_province, postal_code, country) values ('DPaW','DPaW','http://dpaw.wa.gov.au','17 Dick Perry Avenue',' KENSINGTON','WA','6151','AUSTRALIA')"),
        migrations.RunSQL("INSERT INTO catalogue_collaborator (name, position, email, url, phone,fax,hours_of_service,contact_instructions,organization_id) values ('Admin','Admin','','','','','','',1)"),
        migrations.RunSQL("INSERT INTO catalogue_pycswconfig (language, max_records, transactions, allowed_ips, harvest_page_size, title, abstract, keywords, keywords_type,  fees, access_constraints, repository_filter, inspire_enabled, inspire_languages, inspire_default_language, inspire_date, gemet_keywords, conformity_service, temporal_extent_start, temporal_extent_end, point_of_contact_id, service_type_version) values ('en-US',10,false,'127.0.0.1',10,'DPaW','','','discipline',  '','','',false,'','',NULL,'','',NULL,NULL,1,'')"),
    ]
