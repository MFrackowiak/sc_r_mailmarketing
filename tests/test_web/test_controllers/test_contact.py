from urllib.parse import urlencode

from tests.test_web.test_controllers.base import BaseHandlerTest


class TestContactsHandler(BaseHandlerTest):
    def test_get(self):
        self.contact_service.get_contacts_pages_count.return_value = 5

        response = self.fetch("/contacts?page=2", method="GET")

        self.assertEqual(response.code, 200)
        self.contact_service.read_contacts.assert_awaited_once_with(2, 25)
        self.contact_service.get_contacts_pages_count.assert_awaited_once_with(25)
        self.template_loader.load.assert_called_once_with("contacts/contacts.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            objects=self.contact_service.read_contacts.return_value,
            columns=["id", "name", "email"],
            url_base="/contacts/",
            pages={
                "prev": [1],
                "first": False,
                "current": 2,
                "next": [3, 4],
                "last": True,
                "total": 5,
            },
        )

    def test_post(self):
        self.contact_service.create_contact.return_value = {"id": 3}

        response = self.fetch(
            "/contacts",
            method="POST",
            body=urlencode(
                {
                    "name": "test",
                    "email": "test@test.co",
                    "first_name": "Test",
                    "last_name": "Testov",
                }
            ),
            follow_redirects=False,
        )

        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers["location"], "/contacts/3")


class TestContactHandler(BaseHandlerTest):
    def test_get(self):
        response = self.fetch("/contacts/2", method="GET")

        self.assertEqual(response.code, 200)
        self.contact_service.get_contact.assert_awaited_once_with(2)
        self.template_loader.load.assert_called_once_with("contacts/contact.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            contact=self.contact_service.get_contact.return_value
        )

    def test_post(self):
        response = self.fetch(
            "/contacts/2",
            method="POST",
            body=urlencode(
                {
                    "name": "test",
                    "email": "test@test.co",
                    "first_name": "Test",
                    "last_name": "Testov",
                }
            ),
            follow_redirects=False,
        )

        self.assertEqual(response.code, 200)
        self.contact_service.update_contact.assert_awaited_once_with(
            {
                "id": 2,
                "name": "test",
                "email": "test@test.co",
                "first_name": "Test",
                "last_name": "Testov",
            }
        )
        self.contact_service.get_contact.assert_awaited_once_with(2)
        self.template_loader.load.assert_called_once_with("contacts/contact.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            contact=self.contact_service.get_contact.return_value
        )


class TestContactFormHandler(BaseHandlerTest):
    def test_get_to_modify(self):
        response = self.fetch("/contacts/2/edit", method="GET")

        self.assertEqual(response.code, 200)
        self.contact_service.get_contact.assert_awaited_once_with(2)
        self.template_loader.load.assert_called_once_with("contacts/contact_form.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            initial=self.contact_service.get_contact.return_value, action="/contacts/2"
        )

    def test_get_to_create(self):
        response = self.fetch("/contacts/add", method="GET")

        self.assertEqual(response.code, 200)
        self.contact_service.get_contact.assert_not_awaited()
        self.template_loader.load.assert_called_once_with("contacts/contact_form.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            initial={}, action="/contacts"
        )


class TestContactSegmentFormHandler(BaseHandlerTest):
    def test_get(self):
        response = self.fetch("/contacts/2/segments", method="GET")

        self.assertEqual(response.code, 200)
        self.contact_service.read_segments.assert_awaited_once_with(1, None)
        self.template_loader.load.assert_called_once_with(
            "contacts/contact_segment_form.html"
        )
        self.template_loader.load.return_value.generate.assert_called_once_with(
            action="/contacts/2/segments",
            segments=self.contact_service.read_segments.return_value,
        )

    def test_post(self):
        response = self.fetch(
            "/contacts/2/segments",
            method="POST",
            body=urlencode({"segment_id": 12}),
            follow_redirects=False,
        )

        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers["location"], "/contacts/2")
        self.contact_service.add_contact_to_segment.assert_awaited_once_with(12, 2)
