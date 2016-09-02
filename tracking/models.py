from __future__ import unicode_literals, absolute_import
from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from mptt.models import MPTTModel, TreeForeignKey
from json2html import json2html
import os


class CommonFields(models.Model):
    """Fields to be added to all tracking model classes.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    org_unit = models.ForeignKey(
        "registers.OrgUnit", on_delete=models.PROTECT, null=True, blank=True)
    cost_centre = models.ForeignKey(
        "registers.CostCentre", on_delete=models.PROTECT, null=True, blank=True)
    extra_data = JSONField(null=True, blank=True)

    def extra_data_pretty(self):
        if not self.extra_data:
            return self.extra_data
        try:
            return format_html(json2html.convert(json=self.extra_data))
        except Exception as e:
            return repr(e)

    def save(self, *args, **kwargs):
        if self.cost_centre and not self.org_unit:
            self.org_unit = self.cost_centre.org_position
        elif self.cost_centre and self.cost_centre.org_position and self.org_unit not in self.cost_centre.org_position.get_descendants(include_self=True):
            self.org_unit = self.cost_centre.org_position
        super(CommonFields, self).save(*args, **kwargs)

    class Meta:
        abstract = True


# Python 2 can't serialize unbound functions, so here's some dumb glue
def get_photo_path(instance, filename='photo.jpg'):
    return os.path.join('user_photo', '{0}.{1}'.format(instance.id, os.path.splitext(filename)))


def get_photo_ad_path(instance, filename='photo.jpg'):
    return os.path.join('user_photo_ad', '{0}.{1}'.format(instance.id, os.path.splitext(filename)))


@python_2_unicode_compatible
class DepartmentUser(MPTTModel):
    """Represents a Department user. Maps to an object managed by Active Directory.
    """
    ACTIVE_FILTER = {"active": True, "email__isnull": False,
                     "cost_centre__isnull": False, "contractor": False}
    # The following choices are intended to match options in Alesco.
    ACCOUNT_TYPE_CHOICES = (
        (3, 'Agency contract'),
        (0, 'Department fixed-term contract'),
        (1, 'Other'),
        (2, 'Permanent'),
        (4, 'Resigned'),
        (9, 'Role-based account'),
        (8, 'Seasonal'),
        (5, 'Shared account'),
        (6, 'Vendor'),
        (7, 'Volunteer'),
    )
    POSITION_TYPE_CHOICES = (
        (0, 'Full time'),
        (1, 'Part time'),
        (2, 'Casual'),
        (3, 'Other'),
    )
    # These fields are populated from Active Directory.
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    cost_centre = models.ForeignKey(
        "registers.CostCentre", on_delete=models.PROTECT, null=True)
    cost_centres_secondary = models.ManyToManyField(
        "registers.CostCentre", related_name="cost_centres_secondary",
        blank=True)
    org_unit = models.ForeignKey(
        "registers.OrgUnit", on_delete=models.PROTECT, null=True, blank=True,
        verbose_name='organisational unit')
    org_units_secondary = models.ManyToManyField(
        "registers.OrgUnit", related_name="org_units_secondary", blank=True)
    extra_data = JSONField(null=True, blank=True)
    ad_guid = models.CharField(max_length=48, unique=True, editable=False)
    ad_dn = models.CharField(max_length=512, unique=True, editable=False)
    ad_data = JSONField(null=True, editable=False)
    org_data = JSONField(null=True, editable=False)
    employee_id = models.CharField(
        max_length=128, null=True, unique=True, blank=True, verbose_name='Employee ID',
        help_text="HR Employee ID, use 'n/a' if a contractor")
    username = models.CharField(max_length=128, editable=False, unique=True)
    name = models.CharField(max_length=128, help_text='Format: Surname, Given name')
    given_name = models.CharField(
        max_length=128, null=True, help_text='Legal first name (matches birth certificate/password/etc.)')
    surname = models.CharField(
        max_length=128, null=True, help_text='Legal surname (matches birth certificate/password/etc.)')
    name_update_reference = models.CharField(
        max_length=512, null=True, blank=True, verbose_name='update reference',
        help_text='Reference for name/CC change request')
    preferred_name = models.CharField(
        max_length=256, null=True, blank=True, help_text='Employee-editable preferred name.')
    title = models.CharField(
        max_length=128, null=True, help_text='Occupation position title (should match Alesco)')
    position_type = models.PositiveSmallIntegerField(
        choices=POSITION_TYPE_CHOICES, null=True, blank=True, default=0,
        help_text='Employee position working arrangement (should match Alesco status)')
    email = models.EmailField(unique=True, editable=False)
    parent = TreeForeignKey(
        'self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
        editable=True, verbose_name='Reports to', help_text='Person that this employee reports to')
    expiry_date = models.DateTimeField(null=True, editable=False)
    date_ad_updated = models.DateTimeField(null=True, editable=False, verbose_name='Date AD updated')
    telephone = models.CharField(max_length=128, null=True, blank=True)
    mobile_phone = models.CharField(max_length=128, null=True, blank=True)
    home_phone = models.CharField(max_length=128, null=True, blank=True)
    other_phone = models.CharField(max_length=128, null=True, blank=True)
    active = models.BooleanField(default=True, editable=False)
    ad_deleted = models.BooleanField(default=False, editable=False)
    in_sync = models.BooleanField(default=False, editable=False)
    vip = models.BooleanField(
        default=False, help_text="An individual who carries out a critical role for the department")
    executive = models.BooleanField(
        default=False, help_text="An individual who is an executive")
    contractor = models.BooleanField(
        default=False, help_text="An individual who is an external contractor (does not include agency contract staff)")
    photo = models.ImageField(blank=True, upload_to=get_photo_path)
    photo_ad = models.ImageField(
        blank=True, editable=False, upload_to=get_photo_ad_path)
    sso_roles = models.TextField(
        null=True, editable=False, help_text="Groups/roles separated by semicolon")
    notes = models.TextField(
        null=True, blank=True, help_text="Officer secondary roles, etc.")
    working_hours = models.TextField(
        default="N/A", null=True, blank=True, help_text="Description of normal working hours")
    secondary_locations = models.ManyToManyField("registers.Location", blank=True)
    populate_primary_group = models.BooleanField(
        default=True, help_text="If unchecked, user will not be added to primary group email")
    account_type = models.PositiveSmallIntegerField(
        choices=ACCOUNT_TYPE_CHOICES, null=True, blank=True,
        help_text='Employee account status (should match Alesco status)')
    alesco_data = JSONField(
        null=True, blank=True, help_text='Readonly data from Alesco')
    security_clearance = models.BooleanField(
        default=False, verbose_name='security clearance granted',
        help_text='''Security clearance approved by CC Manager (confidentiality
        agreement, referee check, police clearance, etc.''')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        ordering = ('name',)

    def __init__(self, *args, **kwargs):
        super(DepartmentUser, self).__init__(*args, **kwargs)
        # Store the pre-save values of some fields on object init.
        self.__original_given_name = self.given_name
        self.__original_surname = self.surname
        self.__original_employee_id = self.employee_id
        self.__original_cost_centre = self.cost_centre
        self.__original_name = self.name
        self.__original_org_unit = self.org_unit

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.employee_id and self.employee_id.lower() == "n/a":
            self.employee_id = None
        if self.employee_id:
            self.employee_id = "{0:06d}".format(int(self.employee_id))
        self.in_sync = True if self.date_ad_updated else False
        if self.cost_centre and not self.org_unit:
            self.org_unit = self.cost_centre.org_position
        if self.cost_centre:
            self.org_data = self.org_data or {}
            self.org_data["units"] = list(self.org_unit.get_ancestors(include_self=True).values(
                "id", "name", "acronym", "unit_type", "costcentre__code", "costcentre__name", "location__name"))
            self.org_data["unit"] = self.org_data["units"][-1]
            if self.org_unit.location:
                self.org_data["location"] = self.org_unit.location.as_dict()
            if self.org_unit.secondary_location:
                self.org_data[
                    "secondary_location"] = self.org_unit.secondary_location.as_dict()
            for unit in self.org_data["units"]:
                unit["unit_type"] = self.org_unit.TYPE_CHOICES_DICT[
                    unit["unit_type"]]
            self.org_data["cost_centre"] = {
                "name": self.org_unit.name,
                "code": self.cost_centre.code,
                "cost_centre_manager": str(self.cost_centre.manager),
                "business_manager": str(self.cost_centre.business_manager),
                "admin": str(self.cost_centre.admin),
                "tech_contact": str(self.cost_centre.tech_contact),
            }
        self.update_photo_ad()
        super(DepartmentUser, self).save(*args, **kwargs)

    def update_photo_ad(self):
        # Update self.photo_ad to a 240x240 thumbnail >10 kb in size.
        if not self.photo:
            if self.photo_ad:
                self.photo_ad.delete()
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.base import ContentFile

        if hasattr(self.photo.file, 'content_type'):
            PHOTO_TYPE = self.photo.file.content_type

            if PHOTO_TYPE == 'image/jpeg':
                PIL_TYPE = 'jpeg'
            elif PHOTO_TYPE == 'image/png':
                PIL_TYPE = 'png'
            else:
                return
        else:
            PIL_TYPE = 'jpeg'
        # good defaults to get ~10kb JPEG images
        PHOTO_AD_SIZE = (240, 240)
        PIL_QUALITY = 75
        # remote file size limit
        PHOTO_AD_FILESIZE = 10000

        image = Image.open(StringIO(self.photo.read()))
        image.thumbnail(PHOTO_AD_SIZE, Image.LANCZOS)

        # in case we miss 10kb, drop the quality and recompress
        for i in range(12):
            temp_buffer = StringIO()
            image.save(temp_buffer, PIL_TYPE,
                       quality=PIL_QUALITY, optimize=True)
            length = temp_buffer.tell()
            if length <= PHOTO_AD_FILESIZE:
                break
            if PIL_TYPE == 'png':
                PIL_TYPE = 'jpeg'
            else:
                PIL_QUALITY -= 5

        temp_buffer.seek(0)
        self.photo_ad.save(os.path.basename(self.photo.name),
                           ContentFile(temp_buffer.read()), save=False)

    def org_data_pretty(self):
        if not self.org_data:
            return self.org_data
        return format_html(json2html.convert(json=self.org_data))

    def ad_data_pretty(self):
        if not self.ad_data:
            return self.ad_data
        return format_html(json2html.convert(json=self.ad_data))

    def alesco_data_pretty(self):
        if not self.alesco_data:
            return self.alesco_data
        # Manually generate HTML table output, to guarantee field order.
        t = '''<table border="1">
            <tr><th>FIRST_NAME</th><td>{FIRST_NAME}</td></tr>
            <tr><th>SECOND_NAME</th><td>{SECOND_NAME}</td></tr>
            <tr><th>SURNAME</th><td>{SURNAME}</td></tr>
            <tr><th>EMPLOYEE_NO</th><td>{EMPLOYEE_NO}</td></tr>
            <tr><th>PAYPOINT</th><td>{PAYPOINT}</td></tr>
            <tr><th>PAYPOINT_DESC</th><td>{PAYPOINT_DESC}</td></tr>
            <tr><th>MANAGER_POS#</th><td>{MANAGER_POS#}</td></tr>
            <tr><th>MANAGER_NAME</th><td>{MANAGER_NAME}</td></tr>
            <tr><th>JOB_NO</th><td>{JOB_NO}</td></tr>
            <tr><th>FIRST_COMMENCE</th><td>{FIRST_COMMENCE}</td></tr>
            <tr><th>OCCUP_TERM_DATE</th><td>{OCCUP_TERM_DATE}</td></tr>
            <tr><th>POSITION_NO</th><td>{POSITION_NO}</td></tr>
            <tr><th>OCCUP_POS_TITLE</th><td>{OCCUP_POS_TITLE}</td></tr>
            <tr><th>LOC_DESC</th><td>{LOC_DESC}</td></tr>
            <tr><th>CLEVEL1_ID</th><td>{CLEVEL1_ID}</td></tr>
            <tr><th>CLEVEL2_DESC</th><td>{CLEVEL2_DESC}</td></tr>
            <tr><th>CLEVEL3_DESC</th><td>{CLEVEL3_DESC}</td></tr>
            <tr><th>EMP_STAT_DESC</th><td>{EMP_STAT_DESC}</td></tr>
            <tr><th>GEO_LOCATION_DESC</th><td>{GEO_LOCATION_DESC}</td></tr>
            </table>'''
        t = t.format(**self.alesco_data)
        return mark_safe(t)

    @property
    def password_age_days(self):
        from tracking.utils import convert_ad_timestamp  # Prevent circular import.
        if self.ad_data and 'pwdLastSet' in self.ad_data:
            try:
                td = datetime.now() - convert_ad_timestamp(self.ad_data['pwdLastSet'])
                return td.days
            except:
                pass
        return None


@python_2_unicode_compatible
class Computer(CommonFields):
    """Represents a non-mobile computing device. Maps to an object managed by Active Directory.
    """
    sam_account_name = models.CharField(max_length=32, unique=True, null=True)
    hostname = models.CharField(max_length=2048)
    domain_bound = models.BooleanField(default=False)
    ad_guid = models.CharField(max_length=48, null=True, unique=True)
    ad_dn = models.CharField(max_length=512, null=True, unique=True)
    pdq_id = models.IntegerField(null=True, blank=True, unique=True)
    sophos_id = models.CharField(
        max_length=64, unique=True, null=True, blank=True)
    asset_id = models.CharField(
        max_length=64, null=True, blank=True, help_text='OIM Asset ID')
    finance_asset_id = models.CharField(
        max_length=64, null=True, blank=True, help_text='Finance asset ID')
    manufacturer = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    chassis = models.CharField(max_length=128)
    serial_number = models.CharField(max_length=128)
    os_name = models.CharField(max_length=128, blank=True)
    os_version = models.CharField(max_length=128)
    os_service_pack = models.CharField(max_length=128)
    os_arch = models.CharField(max_length=128)
    cpu = models.CharField(max_length=128)
    cpu_count = models.PositiveSmallIntegerField(default=0)
    cpu_cores = models.PositiveSmallIntegerField(default=0)
    memory = models.BigIntegerField(default=0)
    probable_owner = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True,
        related_name='computers_probably_owned',
        help_text='Automatically-generated "most probable" device owner.')
    managed_by = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True,
        related_name='computers_managed',
        help_text='"Official" device owner/manager (set in AD).')
    date_pdq_updated = models.DateTimeField(null=True, blank=True)
    date_nmap_updated = models.DateTimeField(null=True, blank=True)
    date_sophos_updated = models.DateTimeField(null=True, blank=True)
    date_ad_updated = models.DateTimeField(null=True, blank=True)
    date_dhcp_updated = models.DateTimeField(null=True, blank=True)
    # Notes field to store validation results from synchronising
    # user-uploaded local property register spreadsheets.
    validation_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.sam_account_name


@python_2_unicode_compatible
class Mobile(CommonFields):
    """Represents a mobile computing device. Maps to an object managed by Active Directory.
    """
    ad_guid = models.CharField(max_length=48, null=True, unique=True)
    ad_dn = models.CharField(max_length=512, null=True, unique=True)
    registered_to = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True)
    asset_id = models.CharField(
        max_length=64, null=True, help_text='OIM Asset ID')
    finance_asset_id = models.CharField(
        max_length=64, null=True, help_text='Finance asset ID')
    model = models.CharField(max_length=128, null=True)
    os_name = models.CharField(max_length=128, null=True)
    # Identity is a GUID, from Exchange.
    identity = models.CharField(max_length=512, null=True, unique=True)
    serial_number = models.CharField(max_length=128, null=True)
    imei = models.CharField(max_length=64, null=True)
    last_sync = models.DateTimeField(null=True)

    def __str__(self):
        return self.identity


@python_2_unicode_compatible
class EC2Instance(CommonFields):
    """Represents an Amazon EC2 instance.
    """
    name = models.CharField("Instance Name", max_length=200)
    ec2id = models.CharField("EC2 Instance ID", max_length=200, unique=True)
    launch_time = models.DateTimeField(editable=False, null=True, blank=True)
    next_state = models.BooleanField(
        default=True, help_text="Checked is on, unchecked is off")
    running = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'EC2 instance'


@python_2_unicode_compatible
class FreshdeskTicket(models.Model):
    """Cached representation of a Freshdesk ticket, obtained via the
    Freshdesk API.
    """
    # V2 API values below:
    TICKET_SOURCE_CHOICES = (
        (1, 'Email'),
        (2, 'Portal'),
        (3, 'Phone'),
        (7, 'Chat'),
        (8, 'Mobihelp'),
        (9, 'Feedback Widget'),
        (10, 'Outbound Email'),
    )
    TICKET_STATUS_CHOICES = (
        (2, 'Open'),
        (3, 'Pending'),
        (4, 'Resolved'),
        (5, 'Closed'),
    )
    TICKET_PRIORITY_CHOICES = (
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    )
    attachments = JSONField(
        null=True, blank=True, default=list,
        help_text='Ticket attachments. An array of objects.')
    cc_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Email address added in the "cc" field of the incoming ticket email. An array of strings.')
    created_at = models.DateTimeField(null=True, blank=True)
    custom_fields = JSONField(
        null=True, blank=True, default=dict,
        help_text='Key value pairs containing the names and values of custom fields.')
    deleted = models.BooleanField(
        default=False, help_text='Set to true if the ticket has been deleted/trashed.')
    description = models.TextField(
        null=True, blank=True, help_text='HTML content of the ticket.')
    description_text = models.TextField(
        null=True, blank=True, help_text='Content of the ticket in plain text.')
    due_by = models.DateTimeField(
        null=True, blank=True,
        help_text='Timestamp that denotes when the ticket is due to be resolved.')
    email = models.CharField(
        max_length=256, null=True, blank=True, help_text='Email address of the requester.')
    fr_due_by = models.DateTimeField(
        null=True, blank=True,
        help_text='Timestamp that denotes when the first response is due.')
    fr_escalated = models.BooleanField(
        default=False,
        help_text='Set to true if the ticket has been escalated as the result of first response time being breached.')
    fwd_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Email address(e)s added while forwarding a ticket. An array of strings.')
    group_id = models.BigIntegerField(
        null=True, blank=True,
        help_text='ID of the group to which the ticket has been assigned.')
    is_escalated = models.BooleanField(
        default=False,
        help_text='Set to true if the ticket has been escalated for any reason.')
    name = models.CharField(
        max_length=256, null=True, blank=True, help_text='Name of the requester.')
    phone = models.CharField(
        max_length=256, null=True, blank=True, help_text='Phone number of the requester.')
    priority = models.IntegerField(
        null=True, blank=True, help_text='Priority of the ticket.')
    reply_cc_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Email address added while replying to a ticket. An array of strings.')
    requester_id = models.BigIntegerField(
        null=True, blank=True, help_text='User ID of the requester.')
    responder_id = models.BigIntegerField(
        null=True, blank=True, help_text='ID of the agent to whom the ticket has been assigned.')
    source = models.IntegerField(
        null=True, blank=True, help_text='The channel through which the ticket was created.')
    spam = models.BooleanField(
        default=False,
        help_text='Set to true if the ticket has been marked as spam.')
    status = models.IntegerField(
        null=True, blank=True, help_text='Status of the ticket.')
    subject = models.TextField(
        null=True, blank=True, help_text='Subject of the ticket.')
    tags = JSONField(
        null=True, blank=True, default=list,
        help_text='Tags that have been associated with the ticket. An array of strings.')
    ticket_id = models.IntegerField(
        unique=True, help_text='Unique ID of the ticket in Freshdesk.')
    to_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Email addresses to which the ticket was originally sent. An array of strings.')
    type = models.CharField(
        max_length=256, null=True, blank=True, help_text='Ticket type.')
    updated_at = models.DateTimeField(
        null=True, blank=True, help_text='Ticket updated timestamp.')
    # Non-Freshdesk data below.
    freshdesk_requester = models.ForeignKey(
        'FreshdeskContact', on_delete=models.PROTECT, null=True, blank=True,
        related_name='freshdesk_requester')
    freshdesk_responder = models.ForeignKey(
        'FreshdeskContact', on_delete=models.PROTECT, null=True, blank=True,
        related_name='freshdesk_responder')
    du_requester = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True,
        related_name='du_requester',
        help_text='Department User who raised the ticket.')
    du_responder = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True,
        related_name='du_responder',
        help_text='Department User to whom the ticket is assigned.')
    it_system = models.ForeignKey(
        'registers.ITSystem', blank=True, null=True,
        help_text='IT System to which this ticket relates.')

    class Meta:
        # This line is required because we moved this model between apps.
        db_table = 'tracking_freshdeskticket'

    def __str__(self):
        return 'Freshdesk ticket ID {}'.format(self.ticket_id)

    def is_support_category(self, category=None):
        """Returns True if ``support_category`` in the ``custom_fields`` dict
        matches the passed-in value, else False.
        """
        if 'support_category' in self.custom_fields and self.custom_fields['support_category'] == category:
            return True
        return False

    def match_it_system(self):
        """Attempt to locate a matching IT System object to associate with.
        Note that this match will probably stop working whenever anyone alters
        the support_subcategory field values in Freshdesk, so we might need a
        more robust method in future.
        """
        from registers.models import ITSystem
        if self.is_support_category('Applications'):
            if 'support_subcategory' in self.custom_fields and self.custom_fields['support_subcategory']:
                sub = self.custom_fields['support_subcategory']
                # Split on the unicode 'long hyphen':
                if sub.find(u'\u2013') > 0:
                    name = sub.split(u'\u2013')[0].strip()
                    it = ITSystem.objects.filter(name__istartswith=name)
                    if it.count() == 1:  # Matched one IT System by name.
                        self.it_system = it[0]
                        self.save()

    def get_source_display(self):
        """Return the ticket source value description, or None.
        """
        if self.source:
            return next((i[1] for i in self.TICKET_SOURCE_CHOICES if i[0] == self.source), 'Unknown')
        else:
            return None

    def get_status_display(self):
        """Return the ticket status value description, or None.
        """
        if self.status:
            return next((i[1] for i in self.TICKET_STATUS_CHOICES if i[0] == self.status), 'Unknown')
        else:
            return None

    def get_priority_display(self):
        """Return the ticket priority value description, or None.
        """
        if self.priority:
            return next((i[1] for i in self.TICKET_PRIORITY_CHOICES if i[0] == self.priority), 'Unknown')
        else:
            return None


@python_2_unicode_compatible
class FreshdeskConversation(models.Model):
    """Cached representation of a Freshdesk conversation, obtained via the API.
    """
    attachments = JSONField(
        null=True, blank=True, default=list,
        help_text='Ticket attachments. An array of objects.')
    body = models.TextField(
        null=True, blank=True, help_text='HTML content of the conversation.')
    body_text = models.TextField(
        null=True, blank=True, help_text='Content of the conversation in plain text.')
    cc_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Email address added in the "cc" field of the conversation. An array of strings.')
    created_at = models.DateTimeField(null=True, blank=True)
    conversation_id = models.BigIntegerField(
        unique=True, help_text='Unique ID of the conversation in Freshdesk.')
    from_email = models.CharField(max_length=256, null=True, blank=True)
    incoming = models.BooleanField(
        default=False,
        help_text='Set to true if a particular conversation should appear as being created from outside.')
    private = models.BooleanField(
        default=False,
        help_text='Set to true if the note is private.')
    source = models.IntegerField(
        null=True, blank=True, help_text='Denotes the type of the conversation.')
    ticket_id = models.IntegerField(
        help_text='ID of the ticket to which this conversation is being added.')
    to_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Email addresses of agents/users who need to be notified about this conversation. An array of strings.')
    updated_at = models.DateTimeField(
        null=True, blank=True, help_text='Ticket updated timestamp.')
    user_id = models.BigIntegerField(
        help_text='ID of the agent/user who is adding the conversation.')
    # Non-Freshdesk data below.
    freshdesk_ticket = models.ForeignKey(
        FreshdeskTicket, on_delete=models.PROTECT, null=True, blank=True)
    freshdesk_contact = models.ForeignKey(
        'FreshdeskContact', on_delete=models.PROTECT, null=True, blank=True)
    du_user = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True,
        help_text='Department User who is adding to the conversation.')

    class Meta:
        # This line is required because we moved this model between apps.
        db_table = 'tracking_freshdeskconversation'

    def __str__(self):
        return 'Freshdesk conversation ID {}'.format(self.conversation_id)


@python_2_unicode_compatible
class FreshdeskContact(models.Model):
    """Cached representation of a Freshdesk contact, obtained via the API.
    """
    active = models.BooleanField(
        default=False, help_text='Set to true if the contact has been verified.')
    address = models.CharField(max_length=512, null=True, blank=True)
    contact_id = models.BigIntegerField(
        unique=True, help_text='ID of the contact.')
    created_at = models.DateTimeField(null=True, blank=True)
    custom_fields = JSONField(
        null=True, blank=True, default=dict,
        help_text='Key value pairs containing the names and values of custom fields.')
    description = models.TextField(
        null=True, blank=True, help_text='A short description of the contact.')
    email = models.CharField(
        max_length=256, null=True, blank=True, unique=True,
        help_text='Primary email address of the contact.')
    job_title = models.CharField(
        max_length=256, null=True, blank=True, help_text='Job title of the contact.')
    language = models.CharField(
        max_length=256, null=True, blank=True, help_text='Language of the contact.')
    mobile = models.CharField(
        max_length=256, null=True, blank=True, help_text='Mobile number of the contact.')
    name = models.CharField(
        max_length=256, null=True, blank=True, help_text='Name of the contact.')
    other_emails = JSONField(
        null=True, blank=True, default=list,
        help_text='Additional emails associated with the contact. An array of strings.')
    phone = models.CharField(
        max_length=256, null=True, blank=True, help_text='Phone number of the contact.')
    tags = JSONField(
        null=True, blank=True, default=list,
        help_text='Tags that have been associated with the contact. An array of strings.')
    time_zone = models.CharField(
        max_length=256, null=True, blank=True, help_text='Time zone in which the contact resides.')
    updated_at = models.DateTimeField(
        null=True, blank=True, help_text='Contact updated timestamp.')
    # Non-Freshdesk data below.
    du_user = models.ForeignKey(
        DepartmentUser, on_delete=models.PROTECT, blank=True, null=True,
        help_text='Department User that is represented by this Freshdesk contact.')

    class Meta:
        # This line is required because we moved this model between apps.
        db_table = 'tracking_freshdeskcontact'

    def __str__(self):
        return '{} ({})'.format(self.name, self.email)

    def match_dept_user(self):
        """Attempt to locate a matching DepartmentUser object by email.
        """
        if self.email and DepartmentUser.objects.filter(email__iexact=self.email).exists():
            self.du_user = DepartmentUser.objects.get(email__iexact=self.email)
            self.save()
