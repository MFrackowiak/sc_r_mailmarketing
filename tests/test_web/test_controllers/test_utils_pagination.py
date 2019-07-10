from unittest import TestCase

from web.controllers.utils.pagination import create_pagination_context


class PaginationContextTestCase(TestCase):
    def test_0_pages(self):
        self.assertIsNone(create_pagination_context(0, 0))

    def test_1_page(self):
        self.assertIsNone(create_pagination_context(1, 1))

    def test_2_pages(self):
        self.assertEqual(
            {
                "prev": [],
                "first": False,
                "next": [2],
                "current": 1,
                "last": False,
                "total": 2,
            },
            create_pagination_context(1, 2),
        )

    def test_5_pages_current_3(self):
        self.assertEqual(
            {
                "prev": [1, 2],
                "first": False,
                "next": [4, 5],
                "current": 3,
                "last": False,
                "total": 5,
            },
            create_pagination_context(3, 5),
        )

    def test_7_pages_current_4(self):
        self.assertEqual(
            {
                "prev": [2, 3],
                "first": True,
                "next": [5, 6],
                "current": 4,
                "last": True,
                "total": 7,
            },
            create_pagination_context(4, 7),
        )

    def test_7_pages_current_6(self):
        self.assertEqual(
            {
                "prev": [4, 5],
                "first": True,
                "next": [7],
                "current": 6,
                "last": False,
                "total": 7,
            },
            create_pagination_context(6, 7),
        )

    def test_7_pages_current_3(self):
        self.assertEqual(
            {
                "prev": [1, 2],
                "first": False,
                "next": [4, 5],
                "current": 3,
                "last": True,
                "total": 7,
            },
            create_pagination_context(3, 7),
        )
