import tempfile
from os import path

from django import forms
from django.conf import settings
from django.forms.util import ErrorList
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from rosetta import polib, poutil


PO_PROJECT_BASE = 'po_project_base'


class UpdatePoForm(forms.Form):
    file = forms.FileField(label=_('File .po'))
    priority = forms.BooleanField(label=_('Priority'),
        required=False,
        help_text=_('If you check it, your file overwrite the translations, in the other case only will create new entries'))

    def __init__(self, po_file=None, po_file_path=None, *args, **kwargs):
        super(UpdatePoForm, self).__init__(*args, **kwargs)
        self.fields['priority'].is_checkbox = True
        self.data_file = None
        self.po_file = po_file
        self.po_file_path = po_file_path
        if not po_file:
            pofiles_choices = [('', '-----')]
            for language in settings.LANGUAGES:
                pos = poutil.find_pos(language[0], project_apps=True, django_apps=True, third_party_apps=True)
                for po in pos:
                    pofiles_choices.append(tuple((path.realpath(po),
                                                 "%s %s" % (poutil.get_app_name(po), ugettext(language[1])))))

            self.fields['pofile'] = forms.ChoiceField(choices=pofiles_choices, required=False)
            self.fields.keyOrder = ['pofile', 'file', 'priority']

    def clean(self):
        cleaned_data = super(UpdatePoForm, self).clean()
        if not self.po_file_path:
            self.po_file_path = cleaned_data['pofile']
        if not self.po_file:
            self.po_file = polib.pofile(self.po_file_path)
        if not self.errors and not self.po_file:
            try:
                tmp_file, po_tmp, po_dest_file = self._get_files_to_merge()
                tmp_file.close()
            except IOError:
                file_error = self._errors.get('file', ErrorList([]))
                file_error_new = ErrorList([u'Information incompatible for find the destination file'])
                file_error.extend(file_error_new)
                self._errors['file'] = ErrorList(file_error)
        return cleaned_data

    def save_temporal_file(self):
        tmp_file, po_tmp, po_dest_file = self._get_files_to_merge()
        return po_tmp, po_dest_file, self.cleaned_data['priority']

    def _get_files_to_merge(self):
        # Write the user file in a temporal file
        temporal_filepath = tempfile.NamedTemporaryFile().name
        tmp_file = open(temporal_filepath, "w")

        if self.data_file is None:
            self.data_file = self.cleaned_data['file'].read()
        tmp_file.write(self.data_file)
        tmp_file.flush()
        po_tmp = polib.pofile(temporal_filepath)
        return (tmp_file, po_tmp, self.po_file)

    def __unicode__(self):
        try:
            from formadmin.forms import as_django_admin
            return as_django_admin(self)
        except ImportError:
            return super(UpdatePoForm, self).__unicode__()
