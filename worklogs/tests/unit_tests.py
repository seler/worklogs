# -*- coding: utf-8 -*-

import os


from django.conf import settings
from django.utils import unittest
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from django.core.files.storage import get_storage_class

safe_storage = get_storage_class(settings.SAFE_FILE_STORAGE)
storage = safe_storage()

test_loader = unittest.TestLoader()

from ..models import ASPECT_RATIO_CHOICES

ratios = map(lambda l: l[0], ASPECT_RATIO_CHOICES)
aspect_ratio_min_key = lambda x: abs(x - settings.TEST_VIDEO_ASPECT_RATIO)
TEST_VIDEO_ASPECT_RATIO = min(ratios, key=aspect_ratio_min_key)


class TasksTest(unittest.TestCase):

    def setUp(self):
        from ..models import Video
        self.user = User()
        self.user.username = 'scott'
        self.user.active = True
        self.user.set_password('tiger')
        self.user.save()

        self.video = Video()
        self.description = 'Lorem ipsum dolor sit amet. ' * 5
        self.video.title = 'Lipsum'
        self.video.slug = 'lipsum'
        self.video.user = self.user

        self.video.save()

        self.video_file = open(settings.TEST_VIDEO)
        self.video_file_content = ContentFile(self.video_file.read())
        self.video.file.save(os.path.basename(settings.TEST_VIDEO),
                             self.video_file_content)
        self.video.save()
        super(TasksTest, self).setUp()

    def tearDown(self):
        self.video.delete()
        self.user.delete()
        super(TasksTest, self).tearDown()

    def test_retrieve_info(self):
        from ..tasks import retrieve_info
        codec, width, height, duration = retrieve_info(settings.TEST_VIDEO)
        self.assertEqual(width, settings.TEST_VIDEO_WIDTH,
                         msg='incorrect video width')
        self.assertEqual(height, settings.TEST_VIDEO_HEIGHT,
                         msg='incorrect video width')
        self.assertEqual(duration, settings.TEST_VIDEO_DURATION,
                         msg='incorrect video duration')

    def test_capture_frame(self):
        from ..tasks import capture_frame
        filename = capture_frame(settings.TEST_VIDEO, 3.0,
                                 settings.TEST_VIDEO_WIDTH,
                                 settings.TEST_VIDEO_HEIGHT)
        self.assertTrue(os.path.exists(filename))
        # sprzatam
        os.unlink(filename)

    def test_convert_format_default(self):
        from ..tasks import convert_format
        from ..formats import formats_dict
        format = formats_dict[settings.DEFAULT_VIDEO_FORMAT]

        filename = convert_format(settings.TEST_VIDEO,
                                  settings.DEFAULT_VIDEO_FORMAT,
                                  format[TEST_VIDEO_ASPECT_RATIO]['width'],
                                  format[TEST_VIDEO_ASPECT_RATIO]['height'],
                                  format['extension'], format['command'])
        self.assertTrue(os.path.exists(filename), msg='plik nie istnieje')
        os.unlink(filename)

    def test_fetch_file(self):
        from ..tasks import fetch_file
        filename = fetch_file(self.video)
        self.assertTrue(os.path.exists(filename), msg='plik nie istnieje')
        os.unlink(filename)

    def test_clean_files(self):
        from ..tasks import clean_files
        filenames = []
        if not os.path.exists(settings.VIDEO_TMP):
            os.makedirs(settings.VIDEO_TMP)
        for i in range(10):
            filename = os.path.join(settings.VIDEO_TMP, 'test%d' % i)
            filenames.append(filename)
            with open(filename, 'w') as file:
                file.write(filename)
        clean_files(*filenames)
        for filename in filenames:
            self.assertFalse(os.path.exists(filename),
                             msg='plik nie zostal usuniety')

    def test_process_video_task(self):
        u"""
        Sprawdzam, czy film sie konwertuje poprawnie.
        """
        from videos.tasks import process_video_task
        from ..models import Video

        process_video_task(self.video.id)
        video = Video.objects.get(id=self.video.id)
        self.assertEqual(video.width, settings.TEST_VIDEO_WIDTH)
        self.assertEqual(video.height, settings.TEST_VIDEO_HEIGHT)
        self.assertAlmostEqual(video.aspect_ratio,
                               TEST_VIDEO_ASPECT_RATIO,
                               places=2)
        self.assertTrue(storage.exists(video.frame))

    def test_process_video_task_ftp(self):
        u"""
        Sprawdzam, czy film sie konwertuje poprawnie przy pobieraniu z ftp.
        """
        from videos.tasks import process_video_task
        from ..models import Video

        video = Video()
        description = 'Lorem ipsum dolor sit amet. ' * 5
        video.title = 'Lipsum'
        video.slug = 'lipsum'
        video.description = description
        video.user = self.user
        video.file_ftp = os.path.basename(settings.TEST_VIDEO)

        video.save()

        video_file = open(settings.TEST_VIDEO)
        video_file_content = video_file.read()
        ftp_filename = os.path.join(settings.FTP_MEDIA_ROOT, video.file_ftp)
        ftp_file = open(ftp_filename, 'w')
        ftp_file.write(video_file_content)

        process_video_task(self.video.id)
        video = Video.objects.get(id=self.video.id)
        self.assertEqual(video.width, settings.TEST_VIDEO_WIDTH)
        self.assertEqual(video.height, settings.TEST_VIDEO_HEIGHT)
        self.assertAlmostEqual(video.aspect_ratio,
                               TEST_VIDEO_ASPECT_RATIO,
                               places=2)
        self.assertTrue(storage.exists(video.frame))
        os.unlink(ftp_filename)


video_suite = test_loader.loadTestsFromTestCase(TasksTest)


def suite():
    suite = unittest.TestSuite()
    test_suites = [
        video_suite,
    ]
    for test_suite in test_suites:
        suite.addTest(test_suite)
    return suite
