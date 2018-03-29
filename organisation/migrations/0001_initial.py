# Generated by Django 2.0.3 on 2018-03-29 06:27

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import organisation.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CostCentre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=128, unique=True)),
                ('code', models.CharField(max_length=16, unique=True)),
                ('chart_acct_name', models.CharField(blank=True, max_length=256, null=True, verbose_name='chart of accounts name')),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('code',),
            },
        ),
        migrations.CreateModel(
            name='DepartmentUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('extra_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('ad_guid', models.CharField(blank=True, help_text='Locally stored AD GUID. This field must match GUID in the AD object for sync to be successful', max_length=48, null=True, unique=True, verbose_name='AD GUID')),
                ('azure_guid', models.CharField(blank=True, help_text='Azure AD GUID.', max_length=48, null=True, unique=True, verbose_name='Azure GUID')),
                ('ad_dn', models.CharField(blank=True, help_text='AD DistinguishedName value.', max_length=512, null=True, unique=True, verbose_name='AD DN')),
                ('ad_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, editable=False, null=True)),
                ('org_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, editable=False, null=True)),
                ('employee_id', models.CharField(blank=True, help_text='HR Employee ID.', max_length=128, null=True, unique=True, verbose_name='Employee ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(blank=True, editable=False, help_text='Pre-Windows 2000 login username.', max_length=128, null=True)),
                ('name', models.CharField(help_text='Format: [Given name] [Surname]', max_length=128)),
                ('given_name', models.CharField(help_text='Legal first name (matches birth certificate/password/etc.)', max_length=128, null=True)),
                ('surname', models.CharField(help_text='Legal surname (matches birth certificate/password/etc.)', max_length=128, null=True)),
                ('name_update_reference', models.CharField(blank=True, help_text='Reference for name/CC change request', max_length=512, null=True, verbose_name='update reference')),
                ('preferred_name', models.CharField(blank=True, help_text='Employee-editable preferred name.', max_length=256, null=True)),
                ('title', models.CharField(help_text='Occupation position title (should match Alesco)', max_length=128, null=True)),
                ('position_type', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Full time'), (1, 'Part time'), (2, 'Casual'), (3, 'Other')], default=0, help_text='Employee position working arrangement (should match Alesco status)', null=True)),
                ('expiry_date', models.DateTimeField(blank=True, help_text='Date that the AD account is set to expire.', null=True)),
                ('date_ad_updated', models.DateTimeField(editable=False, help_text='The date when the AD account was last updated.', null=True, verbose_name='Date AD updated')),
                ('telephone', models.CharField(blank=True, max_length=128, null=True)),
                ('mobile_phone', models.CharField(blank=True, max_length=128, null=True)),
                ('extension', models.CharField(blank=True, max_length=128, null=True, verbose_name='VoIP extension')),
                ('home_phone', models.CharField(blank=True, max_length=128, null=True)),
                ('other_phone', models.CharField(blank=True, max_length=128, null=True)),
                ('active', models.BooleanField(default=True, editable=False, help_text='Account is active within Active Directory.')),
                ('ad_deleted', models.BooleanField(default=False, editable=False, help_text='Account has been deleted in Active Directory.', verbose_name='AD deleted')),
                ('in_sync', models.BooleanField(default=False, editable=False, help_text='CMS data has been synchronised from AD data.')),
                ('vip', models.BooleanField(default=False, help_text='An individual who carries out a critical role for the department')),
                ('executive', models.BooleanField(default=False, help_text='An individual who is an executive')),
                ('contractor', models.BooleanField(default=False, help_text='An individual who is an external contractor (does not include agency contract staff)')),
                ('photo', models.ImageField(blank=True, upload_to=organisation.utils.get_photo_path)),
                ('photo_ad', models.ImageField(blank=True, editable=False, upload_to=organisation.utils.get_photo_ad_path)),
                ('sso_roles', models.TextField(editable=False, help_text='Groups/roles separated by semicolon', null=True)),
                ('notes', models.TextField(blank=True, help_text='Records relevant to any AD account extension, expiry or deletion (e.g. ticket #).', null=True)),
                ('working_hours', models.TextField(blank=True, default='N/A', help_text='Description of normal working hours', null=True)),
                ('populate_primary_group', models.BooleanField(default=True, help_text='If unchecked, user will not be added to primary group email')),
                ('account_type', models.PositiveSmallIntegerField(blank=True, choices=[(2, 'L1 User Account - Permanent'), (3, 'L1 User Account - Agency contract'), (0, 'L1 User Account - Department fixed-term contract'), (8, 'L1 User Account - Seasonal'), (6, 'L1 User Account - Vendor'), (7, 'L1 User Account - Volunteer'), (1, 'L1 User Account - Other/Alumni'), (11, 'L1 User Account - RoomMailbox'), (12, 'L1 User Account - EquipmentMailbox'), (10, 'L2 Service Account - System'), (5, 'L1 Group (shared) Mailbox - Shared account'), (9, 'L1 Role Account - Role-based account'), (4, 'Terminated'), (14, 'Unknown - AD disabled'), (15, 'Cleanup - Permanent'), (16, 'Unknown - AD active')], help_text='Employee account status (should match Alesco status)', null=True)),
                ('alesco_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='Readonly data from Alesco', null=True)),
                ('security_clearance', models.BooleanField(default=False, help_text='Security clearance approved by CC Manager (confidentiality\n        agreement, referee check, police clearance, etc.', verbose_name='security clearance granted')),
                ('o365_licence', models.NullBooleanField(default=None, editable=False, help_text='Account consumes an Office 365 licence.')),
                ('shared_account', models.BooleanField(default=False, editable=False, help_text='Automatically set from account type.')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('cost_centre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.CostCentre')),
                ('cost_centres_secondary', models.ManyToManyField(blank=True, editable=False, help_text='NOTE: this provides security group access (e.g. T drives).', related_name='cost_centres_secondary', to='organisation.CostCentre')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('address', models.TextField(blank=True, unique=True)),
                ('pobox', models.TextField(blank=True, verbose_name='PO Box')),
                ('phone', models.CharField(blank=True, max_length=128, null=True)),
                ('fax', models.CharField(blank=True, max_length=128, null=True)),
                ('email', models.CharField(blank=True, max_length=128, null=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('url', models.CharField(blank=True, help_text='URL to webpage with more information', max_length=2000, null=True)),
                ('bandwidth_url', models.CharField(blank=True, help_text='URL to prtg graph of bw utilisation', max_length=2000, null=True)),
                ('active', models.BooleanField(default=True)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.DepartmentUser')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='OrgUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_type', models.PositiveSmallIntegerField(choices=[(0, 'Department (Tier one)'), (1, 'Division (Tier two)'), (11, 'Division'), (9, 'Group'), (2, 'Branch'), (7, 'Section'), (3, 'Region'), (6, 'District'), (8, 'Unit'), (5, 'Office'), (10, 'Work centre')])),
                ('ad_guid', models.CharField(editable=False, max_length=48, null=True, unique=True)),
                ('ad_dn', models.CharField(editable=False, max_length=512, null=True, unique=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('acronym', models.CharField(blank=True, max_length=16, null=True)),
                ('details', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('sync_o365', models.BooleanField(default=True, help_text='Sync this to O365 (creates a security group).')),
                ('active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.Location')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.DepartmentUser')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='organisation.OrgUnit')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SecondaryLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('phone', models.CharField(blank=True, max_length=128, null=True)),
                ('fax', models.CharField(blank=True, max_length=128, null=True)),
                ('email', models.CharField(blank=True, max_length=128, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organisation.Location')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.DepartmentUser')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='orgunit',
            name='secondary_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.SecondaryLocation'),
        ),
        migrations.AddField(
            model_name='departmentuser',
            name='org_unit',
            field=models.ForeignKey(blank=True, help_text="The organisational unit that represents the user's primary physical location (also set their distribution group).", null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.OrgUnit', verbose_name='organisational unit'),
        ),
        migrations.AddField(
            model_name='departmentuser',
            name='org_units_secondary',
            field=models.ManyToManyField(blank=True, editable=False, help_text='NOTE: this provides email distribution group access.', related_name='org_units_secondary', to='organisation.OrgUnit'),
        ),
        migrations.AddField(
            model_name='departmentuser',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, help_text='Person that this employee reports to', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='organisation.DepartmentUser', verbose_name='Reports to'),
        ),
        migrations.AddField(
            model_name='departmentuser',
            name='secondary_locations',
            field=models.ManyToManyField(blank=True, help_text='Only to be used for staff working in additional loactions from their cost centre', to='organisation.Location'),
        ),
        migrations.AddField(
            model_name='costcentre',
            name='admin',
            field=models.ForeignKey(blank=True, help_text='Adminstration Officer', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='admin_ccs', to='organisation.DepartmentUser'),
        ),
        migrations.AddField(
            model_name='costcentre',
            name='business_manager',
            field=models.ForeignKey(blank=True, help_text='Business Manager', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bmanage_ccs', to='organisation.DepartmentUser'),
        ),
        migrations.AddField(
            model_name='costcentre',
            name='division',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='costcentres_in_division', to='organisation.OrgUnit'),
        ),
        migrations.AddField(
            model_name='costcentre',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='manage_ccs', to='organisation.DepartmentUser'),
        ),
        migrations.AddField(
            model_name='costcentre',
            name='org_position',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organisation.OrgUnit'),
        ),
        migrations.AddField(
            model_name='costcentre',
            name='tech_contact',
            field=models.ForeignKey(blank=True, help_text='Technical Contact', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tech_ccs', to='organisation.DepartmentUser'),
        ),
    ]
