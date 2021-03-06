from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy, ugettext_noop

from openslides.config.api import ConfigGroup, ConfigGroupedCollection, ConfigVariable

from .models import Group, Permission, User


def setup_users_config(sender, **kwargs):
    """
    Receiver function to setup all users config variables. It is connected
    to the signal openslides.config.signals.config_signal during app loading.
    """
    # General
    users_sort_users_by_first_name = ConfigVariable(
        name='users_sort_users_by_first_name',
        default_value=False,
        form_field=forms.BooleanField(
            required=False,
            label=ugettext_lazy('Sort users by first name'),
            help_text=ugettext_lazy('Disable for sorting by last name')))

    group_general = ConfigGroup(
        title=ugettext_lazy('Sorting'),
        variables=(users_sort_users_by_first_name,))

    # PDF
    users_pdf_welcometitle = ConfigVariable(
        name='users_pdf_welcometitle',
        default_value=_('Welcome to OpenSlides!'),
        translatable=True,
        form_field=forms.CharField(
            widget=forms.Textarea(),
            required=False,
            label=ugettext_lazy('Title for access data and welcome PDF')))

    users_pdf_welcometext = ConfigVariable(
        name='users_pdf_welcometext',
        default_value=_('[Place for your welcome and help text.]'),
        translatable=True,
        form_field=forms.CharField(
            widget=forms.Textarea(),
            required=False,
            label=ugettext_lazy('Help text for access data and welcome PDF')))

    users_pdf_url = ConfigVariable(
        name='users_pdf_url',
        default_value='http://example.com:8000',
        form_field=forms.CharField(
            widget=forms.TextInput(),
            required=False,
            label=ugettext_lazy('System URL'),
            help_text=ugettext_lazy('Used for QRCode in PDF of access data.')))

    users_pdf_wlan_ssid = ConfigVariable(
        name='users_pdf_wlan_ssid',
        default_value='',
        form_field=forms.CharField(
            widget=forms.TextInput(),
            required=False,
            label=ugettext_lazy('WLAN name (SSID)'),
            help_text=ugettext_lazy('Used for WLAN QRCode in PDF of access data.')))

    users_pdf_wlan_password = ConfigVariable(
        name='users_pdf_wlan_password',
        default_value='',
        form_field=forms.CharField(
            widget=forms.TextInput(),
            required=False,
            label=ugettext_lazy('WLAN password'),
            help_text=ugettext_lazy('Used for WLAN QRCode in PDF of access data.')))

    users_pdf_wlan_encryption = ConfigVariable(
        name='users_pdf_wlan_encryption',
        default_value='',
        form_field=forms.ChoiceField(
            widget=forms.Select(),
            required=False,
            label=ugettext_lazy('WLAN encryption'),
            help_text=ugettext_lazy('Used for WLAN QRCode in PDF of access data.'),
            choices=(
                ('', '---------'),
                ('WEP', 'WEP'),
                ('WPA', 'WPA/WPA2'),
                ('nopass', ugettext_lazy('No encryption')))))

    group_pdf = ConfigGroup(
        title=ugettext_lazy('PDF'),
        variables=(users_pdf_welcometitle,
                   users_pdf_welcometext,
                   users_pdf_url,
                   users_pdf_wlan_ssid,
                   users_pdf_wlan_password,
                   users_pdf_wlan_encryption))

    return ConfigGroupedCollection(
        title=ugettext_noop('Users'),
        url='users',
        weight=50,
        groups=(group_general, group_pdf))


def create_builtin_groups_and_admin(**kwargs):
    """
    Creates the builtin groups: Anonymous, Registered, Delegates and Staff.

    Creates the builtin user: admin.
    """
    # Check whether the group pks 1 to 4 are free
    if Group.objects.filter(pk__in=range(1, 5)).exists():
        # Do completely nothing if there are already some of our groups in the database.
        return

    # Anonymous (pk 1) and Registered (pk 2)
    ct_core = ContentType.objects.get(app_label='core', model='customslide')
    perm_11 = Permission.objects.get(content_type=ct_core, codename='can_see_projector')
    perm_12 = Permission.objects.get(content_type=ct_core, codename='can_see_dashboard')

    ct_agenda = ContentType.objects.get(app_label='agenda', model='item')
    ct_speaker = ContentType.objects.get(app_label='agenda', model='speaker')
    perm_13 = Permission.objects.get(content_type=ct_agenda, codename='can_see_agenda')
    perm_14 = Permission.objects.get(content_type=ct_agenda, codename='can_see_orga_items')
    can_speak = Permission.objects.get(content_type=ct_speaker, codename='can_be_speaker')

    ct_motion = ContentType.objects.get(app_label='motion', model='motion')
    perm_15 = Permission.objects.get(content_type=ct_motion, codename='can_see_motion')

    ct_assignment = ContentType.objects.get(app_label='assignment', model='assignment')
    perm_16 = Permission.objects.get(content_type=ct_assignment, codename='can_see_assignments')

    ct_users = ContentType.objects.get(app_label='users', model='user')
    perm_users_can_see_name = Permission.objects.get(content_type=ct_users, codename='can_see_name')
    perm_users_can_see_extra_data = Permission.objects.get(content_type=ct_users, codename='can_see_extra_data')

    ct_mediafile = ContentType.objects.get(app_label='mediafile', model='mediafile')
    perm_18 = Permission.objects.get(content_type=ct_mediafile, codename='can_see')

    base_permission_list = (
        perm_11,
        perm_12,
        perm_13,
        perm_14,
        perm_15,
        perm_16,
        perm_users_can_see_name,
        perm_users_can_see_extra_data,
        perm_18)

    group_anonymous = Group.objects.create(name=ugettext_noop('Anonymous'), pk=1)
    group_anonymous.permissions.add(*base_permission_list)
    group_registered = Group.objects.create(name=ugettext_noop('Registered'), pk=2)
    group_registered.permissions.add(can_speak, *base_permission_list)

    # Delegates (pk 3)
    perm_31 = Permission.objects.get(content_type=ct_motion, codename='can_create_motion')
    perm_32 = Permission.objects.get(content_type=ct_motion, codename='can_support_motion')
    perm_33 = Permission.objects.get(content_type=ct_assignment, codename='can_nominate_other')
    perm_34 = Permission.objects.get(content_type=ct_assignment, codename='can_nominate_self')
    perm_35 = Permission.objects.get(content_type=ct_mediafile, codename='can_upload')

    group_delegates = Group.objects.create(name=ugettext_noop('Delegates'), pk=3)
    group_delegates.permissions.add(perm_31, perm_32, perm_33, perm_34, perm_35)

    # Staff (pk 4)
    perm_41 = Permission.objects.get(content_type=ct_agenda, codename='can_manage_agenda')
    perm_42 = Permission.objects.get(content_type=ct_motion, codename='can_manage_motion')
    perm_43 = Permission.objects.get(content_type=ct_assignment, codename='can_manage_assignments')
    perm_44 = Permission.objects.get(content_type=ct_users, codename='can_manage')
    perm_45 = Permission.objects.get(content_type=ct_core, codename='can_manage_projector')
    perm_46 = Permission.objects.get(content_type=ct_core, codename='can_use_chat')
    perm_47 = Permission.objects.get(content_type=ct_mediafile, codename='can_manage')

    ct_config = ContentType.objects.get(app_label='config', model='configstore')
    perm_48 = Permission.objects.get(content_type=ct_config, codename='can_manage')

    ct_tag = ContentType.objects.get(app_label='core', model='tag')
    can_manage_tags = Permission.objects.get(content_type=ct_tag, codename='can_manage_tags')

    group_staff = Group.objects.create(name=ugettext_noop('Staff'), pk=4)
    # add delegate permissions (without can_support_motion)
    group_staff.permissions.add(perm_31, perm_33, perm_34, perm_35)
    # add staff permissions
    group_staff.permissions.add(perm_41, perm_42, perm_43, perm_44, perm_45, perm_46, perm_47, perm_48, can_manage_tags)
    # add can_see_name and can_see_extra_data permissions
    # TODO: Remove this redundancy after cleanup of the permission system.
    group_staff.permissions.add(perm_users_can_see_name, perm_users_can_see_extra_data)

    # Admin user
    User.objects.create_or_reset_admin_user()
