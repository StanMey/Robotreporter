from django.contrib.auth.models import Group, User
from django.test import Client, TestCase

from articles_app.models import Articles
from http import HTTPStatus
from datetime import datetime


class ViewsTestCase(TestCase):
    """Here all the views are tested that return an actual page (the render function is returned).

    Args:
        TestCase (django.test.TestCase): A subclass of unittest.TestCase
    """
    def setUp(self):
        """Add a user and a group for testing purposes.
        """
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
        """Removes all the SetUp
        """
        self.user1.delete()
        self.user2.delete()
        self.group.delete()

    # home view page
    def test_get_home_view(self):
        """The home page loads properly.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # robots.txt page
    def test_get_robots_txt(self):
        """The robots.txt loads properly.
        """
        response = self.client.get("/robots.txt", follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    # privacy statement page
    def test_get_privacy_statement(self):
        """The privacy statement page loads properly.
        """
        response = self.client.get("/privacy", follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # cookie statement page
    def test_get_cookie_statement(self):
        """The cookie statement page loads properly.
        """
        response = self.client.get("/cookies", follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # moduleA view page
    def test_moduleA_view_user_cannot_access(self):
        """The module A view is prohibited for not logged in users.
        """
        # user is not logged in
        response = self.client.get('/modules/moduleA/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_moduleA_view_user_can_access(self):
        """The module A view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/modules/moduleA/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # moduleB view page
    def test_moduleB_view_user_cannot_access(self):
        """The module B view is prohibited for not logged in users.
        """
        # user is not logged in
        response = self.client.get('/modules/moduleB/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_moduleB_view_user_can_access(self):
        """The module B view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/modules/moduleB/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # moduleC view page
    def test_moduleC_view_user_cannot_access(self):
        """The module C view is prohibited for not logged in users.
        """
        # user is not logged in
        response = self.client.get('/modules/moduleC/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_moduleC_view_user_can_access(self):
        """The module C view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/modules/moduleC/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # moduleD view page
    def test_moduleD_view_user_cannot_access(self):
        """The module D view is prohibited for not logged in users.
        """
        # user is not logged in
        response = self.client.get('/modules/moduleD/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_moduleD_view_user_can_access(self):
        """The module D view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/modules/moduleD/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # relevance view page
    def test_relevance_view_user_cannot_access(self):
        """The relevance view is prohibited for not logged in users."""
        # user is not logged in
        response = self.client.get('/modules/relevance/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_relevance_view_user_can_access(self):
        """The relevance view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get('/modules/relevance/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # single article page
    def test_article_view_user_cannot_access(self):
        """The article view is prohibited for not logged in users.
        """
        # user is not logged in
        response = self.client.get(f"/modules/articles/{self.article.id}")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_article_view_user_can_access(self):
        """The article view can be accessed by logged in users.
        """
        # user is logged in
        response = self.client2.get(f"/modules/articles/{self.article.id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # 3 articles page for not logged in user
    def test_load_latest_articles(self):
        """A not logged in user can access the 3 most recent articles.
        """
        # user is not logged in
        response = self.client.get("/modules/latest/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_load_latest_single_article(self):
        """A not logged in user can access an article.
        """
        # user can access a article
        response = self.client.get("/modules/latest/1")
        self.assertEqual(response.status_code, HTTPStatus.OK)
