# -*- coding: utf-8 -*-
import datetime
import os

from django.conf import settings
#from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.contrib.auth.models import User
from django.utils import unittest

from perf_utils.testcases import AcceptanceTestCase


safe_storage = get_storage_class(settings.SAFE_FILE_STORAGE)
storage = safe_storage()

test_loader = unittest.TestLoader()


class AbstractMuratorTest(AcceptanceTestCase):
    pass


class AddVideoTest(AbstractMuratorTest):
    fixtures = [
            os.path.join(settings.PROJECT_PATH,
                         'fixtures/categories_data.json'),
        ]

    def setUp(self):
        super(AddVideoTest, self).setUp()
        self.username = 'scott'
        self.password = 'tiger'
        self.user = User()
        self.user.username = self.username
        self.user.is_active = True
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.set_password(self.password)
        self.user.save()

        from categories.models import Category
        self.category1 = Category.objects.get(id=1)
        self.category2 = Category.objects.get(id=2)

    def tearDown(self):
        super(AddVideoTest, self).tearDown()

    def test_add_video_admin(self):
        u"""
        Dodawanie filmu w panelu admina standardowo.
        """

        video_title = 'Lorem ipsum'
        video_slug = 'lorem-ipsum'
        video_description = '<p>Lorem ipsum dolor sit amet.</p>'
        video_tags = 'lorem, ipsum'
        video_categories = [self.category1.id, self.category2.id]
        video_active = True
        video_pub_date = datetime.datetime.today()
        video_file = open(settings.TEST_VIDEO)
        video_file_content = video_file.read()
        video_file_filename = os.path.basename(settings.TEST_VIDEO)

        # logowanie admina
        response = self.app.get('/admin/')
        response.form['username'] = self.username
        response.form['password'] = self.password
        response = response.form.submit().follow()
        self.assertEqual(response.status_code, 200)

        # klikanie do forma dodawania filmu
        response = response.click(href='^videos/video/add/$')
        self.assertEqual(response.status_code, 200)

        # wype_nienie forma
        response.form['title'] = video_title
        response.form['slug'] = video_slug
        response.form['active'] = video_active
        response.form['description'] = video_description
        response.form['tags'] = video_tags
        response.form['categories'] = video_categories
        response.form['pub_date_0'] = video_pub_date.strftime('%Y-%m-%d')
        response.form['pub_date_1'] = video_pub_date.strftime('%H:%M:00')
        response.form['file'] = (video_file_filename, video_file_content)

        # mockuje konwertowanie filmu
        from mocker import Mocker
        mocker = Mocker()
        process_video = mocker.replace('videos.models.Video.process_video')
        process_video()
        mocker.result(None)
        mocker.replay()

        response = response.form.submit()

        if response.status_code == 200:
            errors = response.context['adminform'].form.errors
            self.assertEqual(errors, {})
        elif response.status_code == 301:
            response = response.follow()
            self.assertEqual(response.status_code, 200)

        from ..models import Video
        try:
            Video.objects.get(title=video_title, slug=video_slug,
                              active=video_active)
        except Video.DoesNotExist:
            self.fail("dodawanie video sie nie powiodlo")

    def test_add_video_admin_ftp(self):
        u"""
        Dodawanie filmu w panelu admina z ftp.
        """

        video_title = 'Lorem ipsum'
        video_slug = 'lorem-ipsum'
        video_description = '<p>Lorem ipsum dolor sit amet.</p>'
        video_tags = 'lorem, ipsum'
        video_categories = [self.category1.id, self.category2.id]
        video_active = True
        video_pub_date = datetime.datetime.today()
        video_file = open(settings.TEST_VIDEO)
        video_file_content = video_file.read()
        video_file_filename = os.path.basename(settings.TEST_VIDEO)

        # logowanie admina
        response = self.app.get('/admin/')
        response.form['username'] = self.username
        response.form['password'] = self.password
        response = response.form.submit().follow()
        self.assertEqual(response.status_code, 200)

        # klikanie do forma dodawania filmu
        response = response.click(href='^videos/video/add/$')
        self.assertEqual(response.status_code, 200)

        # wype_nienie forma
        response.form['title'] = video_title
        response.form['slug'] = video_slug
        response.form['active'] = video_active
        response.form['description'] = video_description
        response.form['tags'] = video_tags
        response.form['categories'] = video_categories
        response.form['pub_date_0'] = video_pub_date.strftime('%Y-%m-%d')
        response.form['pub_date_1'] = video_pub_date.strftime('%H:%M:00')
        response.form['file'] = (video_file_filename, video_file_content)

        # mockuje konwertowanie filmu
        from mocker import Mocker
        mocker = Mocker()
        process_video = mocker.replace('videos.models.Video.process_video')
        process_video()
        mocker.result(None)
        mocker.replay()

        response = response.form.submit()

        if response.status_code == 200:
            errors = response.context['adminform'].form.errors
            self.assertEqual(errors, {})
        elif response.status_code == 301:
            response = response.follow()
            self.assertEqual(response.status_code, 200)

        from ..models import Video
        video_qs = Video.objects.filter(title=video_title,
                                        slug=video_slug,
                                        active=video_active)
        self.assertTrue(video_qs.exists(),
                        msg="dodawanie video sie nie powiodlo")


add_video_suite = test_loader.loadTestsFromTestCase(AddVideoTest)


class CategoriesTest(AbstractMuratorTest):

    def setUp(self):
        super(CategoriesTest, self).setUp()

        self.user = createUser(1, 'scott', 'tiger', True)

        self.category_1 = createCategory(1, 'test category 1',
                                         'test-category-1', '0001', True)
        self.category_2 = createCategory(2, 'test category 2',
                                         'test-category-2', '0002', True)
        self.category_3 = createCategory(3, 'test category 3',
                                         'test-category-3', '0003', False)

        self.video_1 = createVideo(1, 'test video 1',
                                   'test-video-1', self.user, True)
        self.category_1.videos.add(self.video_1)

    def tearDown(self):
        self.video_1.delete()
        self.category_1.delete()
        self.category_2.delete()
        self.category_3.delete()
        self.user.delete()

        super(CategoriesTest, self).tearDown()

    def test_showpage_basic(self):
        u""" domyslne/poprawne dzialanie """
        response = self.app.get('/biblioteka/')
        self.assertEquals(response.status_code, 200)

categories_suite = test_loader.loadTestsFromTestCase(CategoriesTest)


class CategoryTest(AbstractMuratorTest):

    def setUp(self):
        super(CategoryTest, self).setUp()

        self.user = createUser(1, 'scott', 'tiger', True)

        self.category_1 = createCategory(1, 'test category 1',
                                         'test-category-1', '0001', True)
        self.category_2 = createCategory(2, 'test category 2',
                                         'test-category-2', '0002', True)
        self.category_3 = createCategory(3, 'test category 3',
                                         'test-category-3', '0003', False)

        self.video_1 = createVideo(1, 'test video 1',
                                   'test-video-1', self.user, True)
        self.category_1.videos.add(self.video_1)

    def tearDown(self):
        self.video_1.delete()
        self.category_1.delete()
        self.category_2.delete()
        self.category_3.delete()
        self.user.delete()

        super(CategoryTest, self).tearDown()

    def test_showpage_basic(self):
        u""" domyslne/poprawne dzialanie - z filmami w kategorii """
        response = self.app.get('/biblioteka/test-category-1/')
        self.assertEquals(response.status_code, 200)

    def test_showpage_novideo(self):
        u""" brak film_w w kategorii """
        response = self.app.get('/biblioteka/test-category-2/')
        self.assertEquals(response.status_code, 200)

    def test_showpage_nocategory(self):
        u""" b_edne id kategorii """
        response = self.app.get('/biblioteka/test-category-111/',
                                expect_errors=True)
        self.assertEquals(response.status_code, 404)

    def test_showpage_noactivecategory(self):
        u""" kategoria istnieje, ale nie jest aktywna """
        response = self.app.get('/biblioteka/test-category-3/',
                                expect_errors=True)
        self.assertEquals(response.status_code, 404)

category_suite = test_loader.loadTestsFromTestCase(CategoryTest)


class VideoTest(AbstractMuratorTest):

    def setUp(self):
        super(VideoTest, self).setUp()

        self.user = createUser(1, 'scott', 'tiger', True)

        self.category_1 = createCategory(1, 'test category 1',
                                         'test-category-1', '0001', True)

        self.video_1 = createVideo(1, 'test video 1',
                                   'test-video-1', self.user, True)
        self.category_1.videos.add(self.video_1)

        self.video_2 = createVideo(2, 'test video 2',
                                   'test-video-2', self.user, False)
        self.category_1.videos.add(self.video_2)

    def tearDown(self):
        self.video_1.delete()
        self.category_1.delete()
        self.user.delete()

        super(VideoTest, self).tearDown()

    def test_showpage_basic(self):
        u""" domyslne/poprawne dzialanie """
        response = self.app.get('/biblioteka/test-category-1/test-video-1/1/')
        self.assertEquals(response.status_code, 200)

    def test_showpage_withoutcategory(self):
        u""" domyslne/poprawne dzialanie - w adresie nie podana kategoria """
        response = self.app.get('/biblioteka/test-video-1/1/')
        self.assertEquals(response.status_code, 200)

    def test_showpage_wrongslug(self):
        u""" b__dny slug, wi_c przekierowanie 301 """
        response = self.app.get('/biblioteka/test-category-1/test/1/')
        self.assertEquals(response.status_code, 301)

    def test_showpage_novideo(self):
        u""" film nie istnieje """
        response = self.app.get('/biblioteka/test-category-1/test-video-3/3/',
                                expect_errors=True)
        self.assertEquals(response.status_code, 404)

    def test_showpage_noactivevideo(self):
        u""" film jest nieaktywny """
        response = self.app.get('/biblioteka/test-category-1/test-video-2/2/',
                                expect_errors=True)
        self.assertEquals(response.status_code, 404)

    def test_showpage_comment_basic(self):
        u""" komentarze filmu - domyslne/poprawne dzialanie  """
        response = self.app.get('/biblioteka/test-video-1/1/komentarze/')
        self.assertEquals(response.status_code, 200)

    def test_showpage_comment_wrongslug(self):
        u""" komentarze filmu -  b__dny slug, wi_c przekierowanie 301 """
        response = self.app.get('/biblioteka/test/1/komentarze/')
        self.assertEquals(response.status_code, 301)

    def test_showpage_comment_novideo(self):
        u""" komentarze filmu -  film nie istnieje """
        response = self.app.get('/biblioteka/test-video-3/3/komentarze/',
                                expect_errors=True)
        self.assertEquals(response.status_code, 404)

    def test_showpage_comment_noactivevideo(self):
        u""" komentarze filmu - film jest nieaktywny """
        response = self.app.get('/biblioteka/test-video-2/2/komentarze/',
                                expect_errors=True)
        self.assertEquals(response.status_code, 404)


video_suite = test_loader.loadTestsFromTestCase(VideoTest)


def createUser(id, username, passwd, active):
    user = User()
    user.pk = id
    user.username = username
    user.active = active
    user.set_password(passwd)
    user.save()
    return user


def createCategory(id, name, slug, path, active):
    from categories.models import Category
    category = Category()
    category.pk = id
    category.name = name
    category.slug = slug
    category.path = path
    category.depth = 1
    category.active = active
    category.save()
    return category


def createVideo(id, title, slug, user, active):
    from ..models import Video
    video = Video()
    video.pk = id
    video.title = title
    video.slug = slug
    video.active = active
    video.user = user
    video.pub_date = '2010-01-01 00:00:00'
    video.save()

    video_file = open(settings.TEST_VIDEO)
    video_file_content = ContentFile(video_file.read())
    video.file.save(os.path.basename(settings.TEST_VIDEO),
                                                 video_file_content)
    video.save()

    from ..models import ConvertedVideo
    conv = ConvertedVideo()
    conv.video = video
    conv.format = 1
    conv.save()

    return video


def suite():
    suite = unittest.TestSuite()
    test_suites = [
        categories_suite,
        category_suite,
        video_suite,
        add_video_suite,
    ]
    for test_suite in test_suites:
        suite.addTest(test_suite)
    return suite
