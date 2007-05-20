from django.db import connection
from django import newforms as forms
from django.shortcuts import render_to_response
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser


class URLForm(forms.Form):
    url = forms.URLField(max_length=400)


class OptionsForm(forms.Form):
    screen_size = forms.ChoiceField(initial='any', choices=(
        ('any', "Don't Care"),
        (640, "640x480"),
        (800, "800x600"),
        (1024, "1024x768"),
        (1280, "1280x1024"),
        (1600, "1600x1200"),
        ))
    color_depth = forms.ChoiceField(initial='any', choices=(
        ('any', "Don't Care"),
        (4, "4 Bits (16 Colors)"),
        (8, "8 Bits (256 Colors)"),
        (16, "16 Bits (High Color)"),
        (24, "24 Bits (True Color)"),
        ))
    javascript = forms.ChoiceField(initial='any', choices=(
        ('any', "Don't Care"),
        ('no', "Disabled"),
        ('yes', "Enabled"),
        ))
    java = forms.ChoiceField(initial='any', choices=(
        ('any', "Don't Care"),
        ('no', "Disabled"),
        ('yes', "Enabled"),
        ))
    flash = forms.ChoiceField(initial='any', choices=(
        ('any', "Don't Care"),
        ('no', "Disabled"),
        ('yes', "Enabled"),
        (5, "Version 5"),
        (6, "Version 6"),
        (7, "Version 7"),
        (8, "Version 8"),
        (9, "Version 9"),
        ))
    maximum_wait = forms.ChoiceField(initial=30, choices=(
        (15, "15 minutes"),
        (30, "30 minutes"),
        (60, "1 hour"),
        (120, "2 hours"),
        (240, "4 hours"),
        ))


class BrowserForm(forms.BaseForm):

    errors = {}
    base_fields = forms.forms.SortedDictFromList()

    def __init__(self, os, data=None):
        forms.BaseForm.__init__(self)
        self.parts = 1
        browsers = Browser.objects.select_related()
        os_browsers = browsers.filter(
            factory__operating_system__operating_system_group__name=os,
            disabled=False)
        active_browsers = os_browsers.extra(
            where=['"factories_factory"."last_poll" > NOW() - %s::interval'],
            params=['31d'])
        field_dict = {}
        for browser in active_browsers:
            label = browser.browser_group.name
            if browser.major is not None:
                label += ' ' + str(browser.major)
                if browser.minor is not None:
                    label += '.' + str(browser.minor)
            name = (os + ' ' + label).lower()
            name = name.replace(' ', '_').replace('.', '_')
            if name in field_dict:
                continue
            initial = data is None or (name in data and 'on' in data[name])
            field = forms.BooleanField(label=label, initial=initial)
            field_dict[name] = field
        field_names = field_dict.keys()
        field_names.sort()
        for name in field_names:
            self.fields[name] = field_dict[name]

    def __unicode__(self):
        fields = list(self.fields)
        fields_per_part = (len(fields) + self.parts - 1) / self.parts
        output = []
        for part in range(self.parts):
            output.append('<div style="width:12em;float:left">')
            for index in range(fields_per_part):
                if not fields:
                    break
                field = fields.pop(0)
                output.append(unicode(self[field]) +
                    ' <label for="id_%s">%s</label><br />' % (
                    field, self[field].label))
            output.append('</div>')
        return u'\n'.join(output)


def start(request):
    if request.POST:
        url_form = URLForm(request.POST)
        options_form = OptionsForm(request.POST)
        linux_browsers = BrowserForm('Linux', request.POST)
        windows_browsers = BrowserForm('Windows', request.POST)
        mac_browsers = BrowserForm('Mac OS', request.POST)
    else:
        url_form = URLForm()
        options_form = OptionsForm()
        linux_browsers = BrowserForm('Linux')
        windows_browsers = BrowserForm('Windows')
        mac_browsers = BrowserForm('Mac OS')
    linux_browsers.parts = 4
    query_list = connection.queries
    return render_to_response('start.html', locals())