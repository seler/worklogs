# -*- coding: utf-8 -*-
import unittest


def suite():
    from django.conf import settings
    from django.utils.importlib import import_module
    suite = unittest.TestSuite()
    test_suites = []
    test_types = list(settings.tests_types)
    for test_type in test_types:
        try:
            module = import_module('.%s_tests' % test_type, package=__name__)
        except ImportError:
            pass
        else:
            try:
                test_suites.append(module.suite())
            except AttributeError:
                pass
    for test_suite in test_suites:
        suite.addTest(test_suite)
    return suite
