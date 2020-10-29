from django.contrib.auth.models import Group, User
from django.test import Client, TestCase

from articles_app.models import Articles
from http import HTTPStatus
from datetime import datetime


class ViewsTestCase(TestCase):
    """Here all the views are tested that return an actual page (the render function is returned).

    Args:
        TestCase ([type]): [description]
    """
    def setUp(self):
        """Add a user and a group for testing purposes."""
        # create permission group
        group_name = "view_only"
        self.group = Group(name=group_name)
        self.group.save()

        # add a normal user
        self.user1_name = "John"
        self.user1_mail = "john@gmail.com"
        self.user1_pass = "john1"
        self.user1 = User.objects.create_user(username=self.user1_name, email=self.user1_mail, password=self.user1_pass)

        # add a ('view_only') user
        self.user2_name = "Adam"
        self.user2_mail = "adam@gmail.com"
        self.user2_pass = "adam1"
        self.user2 = User.objects.create_user(username=self.user2_name, email=self.user2_mail, password=self.user2_pass)
        self.user2.groups.add(self.group)

        # add not logged in client
        self.client1 = Client()
        # add a normal logged in client
        self.client2 = Client()
        self.client2.login(username=self.user1_name, password=self.user1_pass)
        # add a 'view_only' logged in client
        self.client3 = Client()
        self.client3.login(username=self.user2_name, password=self.user2_pass)

        # add an article
        self.article = Articles.objects.create(title="beurs update",
                                               content="inhoud hier",
                                               date=datetime.now(),
                                               AI_version=1.1,
                                               author="nieuwsbot",
                                               id=1)

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.group.delete()

    # home view page
    def test_get_home_view(self):
        """The home page loads properly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # robots.txt page
    def test_get_robots_txt(self):
        """The robots.txt loads properly."""
        response = self.client.get("/robots.txt", follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    # module view page
    def test_module_view_user_cannot_access(self):
        """The module view is prohibited for not logged in users."""
        # user is not logged in
        response = self.client.get('/module/overview/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_module_view_user_can_access(self):
        """The module view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/module/overview/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # relevance view page
    def test_relevance_view_user_cannot_access(self):
        """The relevance view is prohibited for not logged in users."""
        # user is not logged in
        response = self.client.get('/module/relevance/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_relevance_view_user_can_access(self):
        """The relevance view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/module/relevance/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # single article page
    def test_article_view_user_cannot_access(self):
        """The article view is prohibited for not logged in users."""
        # user is not logged in
        response = self.client.get(f"/module/articles/{self.article.id}")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_article_view_user_can_access(self):
        """The article view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get(f"/module/articles/{self.article.id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)