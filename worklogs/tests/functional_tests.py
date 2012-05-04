# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.utils import unittest
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from perf_utils.testcases import FunctionalTestCase

from ..models import Video
from django.core.files.storage import get_storage_class

safe_storage = get_storage_class(settings.SAFE_FILE_STORAGE)
storage = safe_storage()

test_loader = unittest.TestLoader()


class AbstractMuratorTest(FunctionalTestCase):
    fixtures = [
            #'portal/fixtures/data.json',
        ]


class VideoTest(AbstractMuratorTest):

    def setUp(self):
        super(VideoTest, self).setUp()
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

    def tearDown(self):
        super(VideoTest, self).tearDown()
        self.video.delete()

video_suite = test_loader.loadTestsFromTestCase(VideoTest)


def suite():
    suite = unittest.TestSuite()
    test_suites = [
        video_suite,
    ]
    for test_suite in test_suites:
        suite.addTest(test_suite)
    return suite
