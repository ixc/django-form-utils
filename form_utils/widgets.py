"""
widgets for django-form-utils

Time-stamp: <2009-11-25 02:54:50 carljm widgets.py>

parts of this code taken from http://www.djangosnippets.org/snippets/934/
 - thanks baumer1122

"""
import os
import posixpath

from PIL import Image

from django import forms
from django.conf import settings
from django.utils.functional import curry
from django.utils.safestring import mark_safe
from django.core.files.uploadedfile import SimpleUploadedFile as UploadedFile

def thumbnail(image_path):
    absolute_url = posixpath.join(settings.MEDIA_URL, image_path)
    return u'<img src="%s" alt="%s" />' % (absolute_url, image_path)

class ImageWidget(forms.FileInput):
    template = '%(input)s<br />%(image)s'

    def __init__(self, attrs=None, template=None):
        if template is not None:
            self.template = template
        super(ImageWidget, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        input_html = super(forms.FileInput, self).render(name, value, attrs)
        file_name = str(value)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        try: # is image
            Image.open(file_path)
            image_html = thumbnail(str(value))
            output = self.template % {'input': input_html,
                                      'image': image_html}
        except IOError: # not image
            output = input_html
        return mark_safe(output)

class ClearableFileInput(forms.MultiWidget):
    default_file_widget_class = forms.FileInput
    template = '%(input)s Clear: %(checkbox)s'
    
    def __init__(self, file_widget=None,
                 attrs=None, template=None):
        if template is not None:
            self.template = template
        file_widget = file_widget or self.default_file_widget_class()
        super(ClearableFileInput, self).__init__(
            widgets=[file_widget, forms.CheckboxInput()],
            attrs=attrs)

    def decompress(self, value):
        # the clear checkbox is never initially checked
        self.value = value
        return [value, None]

    def format_output(self, rendered_widgets):
        if getattr(self, 'value', None):
            return self.template % {'input': rendered_widgets[0],
                                    'checkbox': rendered_widgets[1]}
        return rendered_widgets[0]
