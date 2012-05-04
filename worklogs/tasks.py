# -*- coding: utf-8 -*-
import hashlib
import os
import re
import subprocess
import logging
import urllib
import urllib2

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from urllib import urlopen

from celery.decorators import task

safe_storage_class = get_storage_class(settings.SAFE_FILE_STORAGE)
safe_storage = safe_storage_class()

logger = logging.getLogger(__name__)


def fetch_file(obj):
    filename = obj.file.name
    tmpdir = os.path.join(settings.VIDEO_TMP,
                          hashlib.md5(filename).hexdigest())
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    src = safe_storage.open(filename).read()

    tmp_src_path = os.path.join(tmpdir, os.path.basename(filename))
    tmp_src = open(tmp_src_path, 'wb')
    tmp_src.write(src)
    tmp_src.close()
    return tmp_src_path


def clean_files(*filenames):
    for filename in filenames:
        try:
            os.unlink(filename)
            os.removedirs(os.path.dirname(filename))
        except IOError:
            pass
        except OSError:
            pass


def retrieve_info(filename):
    u"""
    Returns tuple of codec, width and height of given video file
    """
    logger.info('pobieram dane o pliku %s' % filename)
    params = {
        'ffmpeg': getattr(settings, 'FFMPEG', '/usr/bin/ffmpeg'),
        'filename': filename
    }
    command = "{ffmpeg:s} -i {filename:s} 2>&1" \
              "| grep 'Duration\|Video:'".format(**params)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    logger.info(result)

    duration, video = result.splitlines()
    regexp = '\s*Duration[:]{1}\s*(\d{2,5})[:]{1}' \
             '(\d{2})[:]{1}' \
             '(\d{2}[.]{1}\d{2}).*'
    h, m, s = re.match(regexp, duration).groups()

    duration = int(round(float(s) + int(m) * 60 + int(h) * 3600))

    codec, width, height = re.match('^\s*Stream.*Video:\s*([a-zA-Z0-9]*).*,\s*'
                      '([0-9]{3,4})x([0-9]{3,4}).*$', video).groups()
    width = int(width)
    height = int(height)
    if width % 2:
        width += 1
    if height % 2:
        height += 1
    return codec, width, height, duration


def capture_frame(filename, time, width, height):
    logger.info('robie screena z filmu %s' % filename)
    frame_filename = os.path.splitext(filename)[0] + '.jpg'
    params = {
        'ffmpeg': getattr(settings, 'FFMPEG', '/usr/bin/ffmpeg'),
        'filename': filename,
        'time': time,
        'width': width,
        'height': height,
        'frame_filename': frame_filename
    }
    command = "{ffmpeg:s} -i {filename:s} -ss {time} -an -vframes 1 -y -f " \
            "image2 -s {width}x{height} {frame_filename} 2>&1".format(**params)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    logger.info(result)
    return frame_filename


def save_frame(filename, obj):
    # generowanie screena
    frame_filename = capture_frame(filename, obj.frame_time,
                                   obj.width, obj.height)
    frame_file = open(frame_filename)
    frame_file_content = ContentFile(frame_file.read())
    obj.frame.save(os.path.basename(frame_filename), frame_file_content)
    return frame_filename


@task()
def capture_frame_task(object_id):
    # powinno tutaj zostać, bo się nie zaimportuje przy budowaniu
    from .models import Video
    obj = Video.objects.get(id=object_id)

    # pobieram plik do tempa
    filename = fetch_file(obj)

    # kasuje stary frame
    obj.frame.delete()

    # generowanie screena
    frame_filename = save_frame(filename, obj)

    # zapisanie całości zmian
    obj.save()

    # sprzątnięcie zbędnych plików w tempie
    clean_files(frame_filename)


def convert_format(filename, format_id, width, height, ext, command):
    logger.info('konwertuje do formatu %d' % format_id)
    format_filename = os.path.splitext(filename)[0] + str(format_id) + ext
    params = {
        'ffmpeg': getattr(settings, 'FFMPEG', '/usr/bin/ffmpeg'),
        'filename': filename,
        'format_filename': format_filename,
        'format_width': width,
        'format_height': height,
    }
    command = command.format(**params)
    process = subprocess.Popen(command + ' 2>&1', shell=True,
                               stdout=subprocess.PIPE)
    result = process.communicate()[0]
    logger.info(result)
    return format_filename


def save_format(format, filename, obj, width, height, ext, command):
    from videos.models import ConvertedVideo
    format_filename = convert_format(filename, format,
                                     width,
                                     height,
                                     ext, command)
    converted_video = ConvertedVideo(video=obj, format=format)
    format_file = open(format_filename)
    format_file_content = ContentFile(format_file.read())
    converted_video.file.save(os.path.basename(format_filename),
                              format_file_content)
    converted_video.save()
    return format_filename


def save_formats(formats, filename, obj):
    # generowanie formatów video
    from .formats import formats_dict
    format_filenames = []
    for i, d in formats_dict.items():
        obj_formats_qs = obj.converted_videos.all()
        obj_formats = obj_formats_qs.values_list('format', flat=True)
        if i in formats and i not in obj_formats:
            format_width = d[obj.aspect_ratio]['width']
            format_height = d[obj.aspect_ratio]['height']
            if format_width <= obj.width and format_height <= obj.height:
                format_filename = save_format(i, filename, obj,
                                              format_width,
                                              format_height,
                                              d['extension'],
                                              d['command'])
                format_filenames.append(format_filename)
            else:
                converted_formats = obj.converted_videos.all() \
                                       .values_list('format', flat=True)
                if d['fallback'] not in converted_formats + [None, ]:
                    format_filenames += save_formats((d['fallback'],),
                                                      filename, obj)
    return format_filenames


def fetch_file_ftp(obj):
    ftp_file = open(os.path.join(settings.FTP_MEDIA_ROOT, obj.file_ftp))
    ftp_file_content = ftp_file.read()
    obj.file.save(obj.file_ftp, ContentFile(ftp_file_content))
    tmpdir = os.path.join(settings.VIDEO_TMP,
                          hashlib.md5(obj.file_ftp).hexdigest())
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    tmp_src_path = os.path.join(tmpdir, os.path.basename(obj.file_ftp))
    tmp_src = open(tmp_src_path, 'wb')
    tmp_src.write(ftp_file_content)
    tmp_src.close()
    return tmp_src_path


@task()
def process_video_task(object_id, formats=None):
    if formats is None:
        formats = (settings.DEFAULT_VIDEO_FORMAT,)

    # powinno tutaj zostac, zeby sie nie importowalo przy budowaniu
    from .models import Video
    try:
        obj = Video.objects.get(id=object_id)
    except Video.DoesNotExist, exc:
        process_video_task.retry(exc=exc, countdown=30)

    # pobieram plik do tempa
    filename = fetch_file(obj)

    # pobieram info o pliku
    codec, width, height, duration = retrieve_info(filename)
    obj.codec = codec
    obj.width = width
    obj.height = height
    obj.duration = duration
    obj.aspect_ratio = obj._calculate_ratio()

    # generowanie screena
    frame_filename = save_frame(filename, obj)

    # zapisanie całości zmian
    obj.save()

    # generowanie formatów video
    format_filenames = save_formats(formats, filename, obj)

    # sprzątnięcie zbędnych plików w tempie
    clean_files(filename, frame_filename, *format_filenames)


class VideoAlreadyExists(Exception):
    pass


@task
def add_video_task(id=None, active=False, category_ids=None, description=None,
               file_url=None, frame_time=3.0, rating_avg=None, title=None,
               rating_count=0, slug=None, tags=None, user_id=None,
               add_date=None, hits=0, author_names=None, highlighted=False,
               imported=False, id_se=None, process=False):
    from .models import Video
    from categories.models import Category
    from cms_local.models import SEImportedVideo

    files_to_delete = []

    video = Video()
    if id:
        video.id = id
        if Video.objects.filter(id=id).exists():
            raise VideoAlreadyExists('film o id %d juz istnieje' % id)
    video.active = active
    video.description = description
    video.frame_time = frame_time
    if slug is None:
        from murator_common.util.slughifi import slughifi
        slug = slughifi(title)
    video.slug = slug
    video.title = title
    video.tags = tags
    video.user_id = user_id
    video.hits = hits
    video.highlighted = highlighted
    video.imported = imported
    video.add_date = add_date
    video.pub_date = add_date

    # pobieram plik do tempa
    tmpdir = os.path.join(settings.VIDEO_TMP,
                          hashlib.md5(file_url).hexdigest())
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    from urllib import urlopen
    response = urlopen(file_url)
    video_file_content = response.read()
    tmp_src_path = os.path.join(tmpdir, os.path.basename(file_url))
    tmp_src = open(tmp_src_path, 'wb')
    tmp_src.write(video_file_content)
    tmp_src.close()
    video.file.save(os.path.basename(tmp_src_path),
                    ContentFile(video_file_content))

    video_filename = tmp_src_path

    files_to_delete.append(video_filename)

    video.save()

    if id_se:
        seiv = SEImportedVideo(id_se=id_se, video=video)
        seiv.save()

    for category_id in category_ids:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            # TODO: moze logowac?
            pass
        else:
            video.categories.add(category)

    for author_name in author_names:
        from authors.models import Author
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            author = Author(name=author_name, real_name=author_name)
            author.save()
        finally:
            video.authors.add(author)

    for i in range(rating_count):
        video.rating.add(score=rating_avg, user=None, ip_address='127.0.0.1')

    video.save()

    if process:
        # TODO: przekopiowac pare rzeczy z process_video_task

        # pobieram info o pliku
        codec, width, height, duration = retrieve_info(video_filename)
        video.codec = codec
        video.width = width
        video.height = height
        video.aspect_ratio = video._calculate_ratio()

        # generowanie screena
        frame_filename = save_frame(video_filename, video)
        files_to_delete.append(frame_filename)

        # zapisanie całości zmian
        video.save()

        # generowanie formatów video
        formats = (settings.DEFAULT_VIDEO_FORMAT,)
        format_filenames = save_formats(formats, video_filename, video)
        files_to_delete += format_filenames

    # sprzątnięcie zbędnych plików w tempie
    clean_files(*files_to_delete)


@task
def test_task(i):
    from time import sleep
    sleep(i % 5)
    return i % 5


@task
def process_video_ftp_task(object_id, formats=None):
    from .models import Video
    try:
        obj = Video.objects.get(id=object_id)
    except Video.DoesNotExist, exc:
        process_video_ftp_task.retry(exc=exc, countdown=30)

    ftp_file = open(os.path.join(settings.FTP_MEDIA_ROOT, obj.file_ftp))
    ftp_file_content = ftp_file.read()
    obj.file.save(obj.file_ftp, ContentFile(ftp_file_content))
    obj.save()

    process_video_task.delay(object_id, formats=formats)


@task
def import_video_task(object_id, frame_time=3.0, thumb_url=None, file_url=None, version_lst=[]):

    from .models import Video
    try:
        video = Video.objects.get(id=object_id)
    except Video.DoesNotExist, exc:
        import_video_task.retry(exc=exc, countdown=30)

    video.ready = False
    video.save()

    if file_url is None and len(version_lst) == 0:
        return

    files_to_delete = []

    if thumb_url:
        # przekopiuj miniaturke
        try:
            response = urllib2.urlopen(thumb_url)
        except urllib2.URLError:
            # utworz miniaturke
            thumb_url = None
        else:
            frame_file_content = ContentFile(response.read())
            video.frame.save(os.path.basename(thumb_url), frame_file_content)

    if file_url:
        video_filename = get_file_to_tmp(file_url, video)
        files_to_delete.append(video_filename)

        # pobieram info o pliku
        codec, width, height, duration = retrieve_info(video_filename)
        video.codec = codec
        video.width = width
        video.height = height
        if not video.duration:
            video.duration = duration
        video.aspect_ratio = video._calculate_ratio()

        if not thumb_url and not video.frame:
            # utworz miniaturke
            frame_filename = save_frame(video_filename, video)
            files_to_delete.append(frame_filename)
        video.save()

        format_filenames = create_formats(video, video_filename)
        files_to_delete += format_filenames

    if version_lst:
        from .formats import formats_dict

        compare_value = lambda id: formats_dict[id][1.78]['width']
        best = None
        for version in version_lst:
            for format_id, format_data in formats_dict.items():
                if version['format'] == format_data['slug']:
                    version['format_id'] = format_id

            if best is None:
                best = format_id
            else:
                if compare_value(format_id) > compare_value(best):
                    best = format_id

        for index, version in enumerate(version_lst):

            if version['format_id'] == best and not file_url and not video.width:
                video_filename = get_file_to_tmp(version['url'], video)
                files_to_delete.append(video_filename)
                codec, width, height, duration = retrieve_info(video_filename)
                video.width = width
                video.height = height
                if not video.duration:
                    video.duration = duration
                video.aspect_ratio = video._calculate_ratio()

                if not thumb_url and not video.frame and not file_url:
                    # utworz miniaturke
                    frame_filename = save_frame(video_filename, video)
                    files_to_delete.append(frame_filename)
                video.save()

            # sciagnij plik
            from videos.models import ConvertedVideo
            converted_video = ConvertedVideo(video=video,
                                             format=version['format_id'])
            response = urlopen(version['url'])
            file_content = response.read()
            format_file_content = ContentFile(file_content)
            converted_video.file.save(os.path.basename(version['url']),
                                      format_file_content)
            converted_video.save()

    # sprzątnięcie zbędnych plików w tempie
    clean_files(*files_to_delete)

    video.ready = True
    video.save()


def get_file_to_tmp(file_url, video):
    """ pobieranie plik do tempa """
    tmpdir = os.path.join(settings.VIDEO_TMP,
                          hashlib.md5(file_url).hexdigest())
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    response = urlopen(file_url)
    video_file_content = response.read()
    tmp_src_path = os.path.join(tmpdir, os.path.basename(file_url))
    tmp_src = open(tmp_src_path, 'wb')
    tmp_src.write(video_file_content)
    tmp_src.close()
    video.file.save(os.path.basename(tmp_src_path),
                    ContentFile(video_file_content))
    video.save()
    return tmp_src_path


def create_formats(video, video_filename):
    u""" generowanie formatów video """
    formats = (settings.DEFAULT_VIDEO_FORMAT,)
    format_filenames = save_formats(formats, video_filename, video)
    return format_filenames
