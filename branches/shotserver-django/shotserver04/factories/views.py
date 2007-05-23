from django.db import connection
from django.http import Http404
from django.shortcuts import render_to_response
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser

FACTORY_LIST_COLUMNS = (
    ('name', _('Name')),
    ('operating_system', _('Operating<br />system')),
    ('architecture', _('Architecture')),
    ('last_poll', _('Last<br />poll')),
    ('last_upload', _('Last<br />upload')),
    ('uploads_per_hour', _('Uploads<br />per hour')),
    ('uploads_per_day', _('Uploads<br />per day')),
)


def factory_list(request):
    order = request.GET.get('order', '')
    if order.lstrip('-') not in FACTORY_LIST_COLUMNS:
        order = '-uploads_per_day'
    order_column = order.lstrip('-')
    descending = order.startswith('-')
    header_list = []
    for column, text in FACTORY_LIST_COLUMNS:
        class_attrib = ''
        if column == order_column:
            found = True
            if descending:
                class_attrib = ' class="sorted descending"'
                url = '?order=' + column
            else:
                class_attrib = ' class="sorted ascending"'
                url = '?order=-' + column
        else:
            url = '?order=' + column
        header_list.append({'text': text,
                            'url': url,
                            'class_attrib': class_attrib})
    factory_list = list(Factory.objects.select_related().order_by(
        order, 'name'))
    query_list = connection.queries
    return render_to_response('factories/factory_list.html', locals())


def factory_detail(request, factory_name):
    try:
        factory = Factory.objects.get(name=factory_name)
    except Factory.DoesNotExist:
        raise Http404
    browser_list = Browser.objects.select_related().filter(factory=factory.id)
    screensize_list = factory.screensize_set.all()
    colordepth_list = factory.colordepth_set.all()
    query_list = connection.queries
    return render_to_response('factories/factory_detail.html', locals())
