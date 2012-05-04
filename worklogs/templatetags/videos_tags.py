#-*- coding: utf-8 -*-


from django.conf import settings
from django.template import Library

from categories.models import Category
from videos.models import Video
register = Library()


@register.inclusion_tag('videos/block/category_menu.html', takes_context=True)
def category_menu(context, active_category=None):
    url_get = context.get('url_get', '')

    categories = Category.objects.filter(show_in_menu=True, active=True)
    ret = {
        'categories': categories,
        'active_category': active_category,
        'url_get': url_get
    }
    return ret


@register.simple_tag
def create_category_option():
    cat_lst = Category.objects.filter(show_in_menu=True, active=True)
    code = ''
    for cat in cat_lst:
        code = '%s<option value="%s">%s</option>' % (code, cat.id, cat.name)
    return code


@register.inclusion_tag('videos/block/video_elem_tile.html', takes_context=True)
def last_video_in_category(context, category_id, category_slug, show_stats=False):
    video_qs = Video.objects.published().filter(categories__id=category_id)
    video_qs = video_qs.order_by('-pub_date')[:1]

    if video_qs.exists():
        video = video_qs.get()

        ret = {
            'video': video,
            'category_id': category_id,
            'category_slug': category_slug,
            'show_stats': show_stats
        }
        return ret


@register.inclusion_tag('videos/block/paginator.html', takes_context=True)
def video_pagination(context, page_obj, paginator):
    page_range = paginator.page_range
    all_page = len(page_range)
    index = page_range.index(page_obj.number) + 1
    start = index - 3
    stop = index + 2
    if start < 0:
        stop = stop - start
        start = 0
        if stop > all_page:
            stop = all_page
    elif stop > all_page:
        start = start - (stop - all_page)
        stop = all_page
        if start < 0:
            start = 0
    num_pages = page_range[start:stop]

    url_get = context.get('url_get', '')
    path = context.get('path', '')
    ret = {
        'num_pages': num_pages,
        'current_page': page_obj.number,
        'all_pages': all_page,
        'url_get': url_get,
        'path': path
    }
    return ret


@register.inclusion_tag('videos/block/rating.html', takes_context=True)
def rating_vote(context, video, request, range_vote=5):
    user = request.user
    ip = request.META['REMOTE_ADDR']
    ret = {
        'object': video,
        'range_arr': range(range_vote),
        'user': user,
        'ip': ip
    }
    return ret


@register.simple_tag
def video_get_url(video, category_slug=None):
    return video.get_absolute_url(category_slug)


@register.simple_tag
def video_in_category_count(category):
    cnt = Video.objects.published().filter(categories=category).count()
    sufix = 'filmów'
    if cnt == 1:
        sufix = 'film'
    else:
        mod100 = cnt % 100
        mod10 = cnt % 10
        if (mod10 == 2 and mod100 != 12) \
                or (mod10 == 3 and mod100 != 13) \
                or (mod10 == 4 and mod100 != 14):
            sufix = 'filmy'
    return "%s %s" % (cnt, sufix)


@register.inclusion_tag('videos/block/show_flowplayer.html', takes_context=True)
def show_flowplayer(context, object):
    img = ''
    if object.frame:
        img = object.frame.url
    flv = ''
    if object.get_converted_video().file:
        flv = object.get_converted_video().file.url
    width = object.get_player_width()
    height = object.get_player_height()
    STATIC_URL = settings.STATIC_URL
    request = context['request']
    ret = {
        'id': object.id,
        'img': img,
        'flv': flv,
        'width': width,
        'height': height,
        'adv_cat': '',
        'adv_scat': '',
        'request': request,
        'STATIC_URL': STATIC_URL
    }
    return ret


@register.filter
def reorder_for_user(value, user_id):
    if user_id == 1:
        return value
    else:
        vlist = []
        for i in value:
            if i.user_id == user_id:
                vlist.append(i)
        return vlist


@register.filter
def get_range(value):
    return range(value)


