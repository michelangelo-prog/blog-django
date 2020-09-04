from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from blog_app.blog.factories import PostFactory, CommentFactory
from blog_app.blog.models import Post
from django.urls import reverse
from django.utils import timezone


class PostMixin:
    def _create_posts_with_past_publish_date_and_status_published(
        self, number_of_posts
    ):
        return [
            PostFactory(
                publish_date=timezone.now() - timedelta(days=i + 1),
                status=Post.STATUS.PUBLISH,
            )
            for i in range(number_of_posts)
        ]

    def _create_posts_with_past_publish_date_and_with_status_draft(
        self, number_of_posts
    ):
        return [
            PostFactory(
                publish_date=timezone.now() - timedelta(days=i + 1),
                status=Post.STATUS.DRAFT,
            )
            for i in range(number_of_posts)
        ]

    def _create_posts_with_future_publish_date_and_status_published(
        self, number_of_posts
    ):
        return [
            PostFactory(
                publish_date=timezone.now() + timedelta(days=i + 1),
                status=Post.STATUS.PUBLISH,
            )
            for i in range(number_of_posts)
        ]

    def _create_posts_with_future_publish_date_and_status_draft(self, number_of_posts):
        return [
            PostFactory(
                publish_date=timezone.now() + timedelta(days=i + 1),
                status=Post.STATUS.DRAFT,
            )
            for i in range(number_of_posts)
        ]

    def _assert_dates(self, date, string):
        self.assertEqual(
            (date + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S"), string
        )

    def _create_unpublished_posts(self):
        return (
            self._create_posts_with_past_publish_date_and_with_status_draft(1)
            + self._create_posts_with_future_publish_date_and_status_published(1)
            + self._create_posts_with_future_publish_date_and_status_draft(1)
        )


class PostListTests(PostMixin, APITestCase):
    def setUp(self) -> None:
        self.domain = "http://testserver"
        self.number_of_posts = 1
        self.number_of_published_posts = 13
        self.published_posts = self._create_posts_with_past_publish_date_and_status_published(
            self.number_of_published_posts
        )
        self._create_posts_with_past_publish_date_and_with_status_draft(
            self.number_of_posts
        )
        self._create_posts_with_future_publish_date_and_status_published(
            self.number_of_posts
        )
        self._create_posts_with_future_publish_date_and_status_draft(
            self.number_of_posts
        )

    def _compare_post_list_data(self, expected_data, received_data):
        expected_fields = {"slug", "title", "summary", "publish_date"}
        for expected, received in zip(expected_data, received_data):
            self.assertSetEqual(expected_fields, set(received.keys()))
            self.assertEqual(expected.slug, received["slug"])
            self.assertEqual(expected.title, received["title"])
            self.assertEqual(expected.summary, received["summary"])
            self._assert_dates(expected.publish_date, received["publish_date"])

    def test_get_only_published_posts(self):
        response = self.client.get(reverse("api_v1:posts"))
        json = response.json()

        self.assertEqual(len(self.published_posts), len(json))

        self._compare_post_list_data(self.published_posts, json)

    def _change_post_status_to_draft(self, posts):
        for post in posts:
            post.status = Post.STATUS.DRAFT
            post.save()

    def test_get_empty_json_when_no_posts_published(self):
        self._change_post_status_to_draft(self.published_posts)
        response = self.client.get(reverse("api_v1:posts"))
        json = response.json()
        self.assertEqual(0, len(json))

    def _get_full_path(self, path, parameters=None):
        if parameters:
            para = "&".join(
                "{}={}".format(key, parameters[key]) for key in parameters.keys()
            )
            return "{}{}?{}".format(self.domain, path, para)
        else:
            return "{}{}".format(self.domain, path)

    def test_get_first_six_published_posts(self):
        parameters = {"limit": 6, "offset": 0}
        path = reverse("api_v1:posts")
        response = self.client.get(path, parameters)
        json = response.json()
        self.assertEqual(self.number_of_published_posts, json["count"])
        self.assertEqual(
            "{}{}?limit={}&offset={}".format(
                self.domain, path, parameters["limit"], parameters["limit"]
            ),
            json["next"],
        )
        self.assertEqual(None, json["previous"])
        self.assertEqual(parameters["limit"], len(json["results"]))
        self._compare_post_list_data(
            self.published_posts[: parameters["limit"]], json["results"]
        )

    def test_get_second_six_published_posts(self):
        parameters = {"limit": 6, "offset": 6}
        path = reverse("api_v1:posts")
        response = self.client.get(path, parameters)
        json = response.json()
        self.assertEqual(self.number_of_published_posts, json["count"])
        self.assertEqual(
            self._get_full_path(
                path, {"limit": parameters["limit"], "offset": parameters["limit"] * 2}
            ),
            json["next"],
        )
        self.assertEqual(
            self._get_full_path(path, {"limit": parameters["limit"]}), json["previous"]
        )
        self.assertEqual(parameters["limit"], len(json["results"]))
        self._compare_post_list_data(
            self.published_posts[parameters["limit"] : parameters["limit"] * 2],
            json["results"],
        )

    def test_get_last_page_of_published_posts(self):
        parameters = {"limit": 6, "offset": 12}
        path = reverse("api_v1:posts")
        response = self.client.get(path, parameters)
        json = response.json()
        expected_number_of_posts = self.number_of_published_posts % parameters["limit"]
        self.assertEqual(self.number_of_published_posts, json["count"])
        self.assertEqual(None, json["next"])
        self.assertEqual(
            self._get_full_path(
                path, {"limit": parameters["limit"], "offset": parameters["limit"]}
            ),
            json["previous"],
        )
        self.assertEqual(expected_number_of_posts, len(json["results"]))
        self._compare_post_list_data(
            self.published_posts[-expected_number_of_posts:], json["results"]
        )


class PostTest(PostMixin, APITestCase):

    def setUp(self) -> None:
        self.number_of_published_posts = 3
        self.published_posts = self._create_posts_with_past_publish_date_and_status_published(
            self.number_of_published_posts
        )
        self.unpublished_posts = self._create_unpublished_posts()

    def test_get_published_post(self):
        post = self.published_posts[2]
        path = reverse("api_v1:post", args=(post.slug,))
        response = self.client.get(path)
        json = response.json()

        self.assertEqual(post.title, json["title"])
        self.assertEqual(post.summary, json["summary"])
        self.assertEqual(post.content, json["content"])
        self._assert_dates(post.publish_date, json["publish_date"])

    def test_404_when_request_unpublished_post(self):
        for post in self.unpublished_posts:
            path = reverse("api_v1:post", args=(post.slug,))
            response = self.client.get(path)
            json = response.json()
            expected_json = {"detail": "Not found."}
            self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
            self.assertEqual(expected_json, json)

    def test_404_when_request_not_existed_post(self):
        slug = "testtesttest"
        path = reverse("api_v1:post", args=(slug,))
        response = self.client.get(path)
        json = response.json()
        expected_json = {"detail": "Not found."}
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_json, json)


class CommentsListTest(PostMixin, APITestCase):

    def _create_comments_with_past_publish_date(self, post, published, number_of_comments):
        return [
            CommentFactory(
                post=post, published=published,
                publish_date=timezone.now() - timedelta(days=i + 1)
            )
            for i in range(number_of_comments)
        ]

    def _create_comments_with_future_publish_date(self, post, published, number_of_comments):
        return [
            CommentFactory(
                post=post, published=published,
                publish_date=timezone.now() + timedelta(days=i + 1)
            )
            for i in range(number_of_comments)
        ]

    def _create_unpublished_comments(self, post):
        return (
            self._create_comments_with_past_publish_date(post, False, 1)
            + self._create_comments_with_future_publish_date(post, True, 1)
            + self._create_comments_with_future_publish_date(post, False, 1)
        )

    def setUp(self) -> None:
        self.number_of_posts = 3
        self.posts = self._create_posts_with_past_publish_date_and_status_published(self.number_of_posts)

        self.post_1 = self.posts[0]
        self.number_of_post_1_published_comments = 3
        self.post_1_published_comments = self._create_comments_with_past_publish_date(self.post_1, True,
                                                                                      self.number_of_post_1_published_comments)
        self._create_unpublished_comments(self.post_1)

        self.post_2 = self.posts[1]
        self._create_unpublished_comments(self.post_2)

        self.unpublished_posts = self._create_unpublished_posts()

    def test_get_comments_for_published_post(self):
        path = reverse("api_v1:post_comments", args=(self.post_1.slug,))
        response = self.client.get(path)
        json = response.json()

        expected_comment_fields = {"name", "body", "publish_date"}

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.number_of_post_1_published_comments, len(json))
        for expected, data in zip(self.post_1_published_comments, json):
            self.assertSetEqual(expected_comment_fields, set(data.keys()))
            self.assertEqual(expected.name, data["name"])
            self.assertEqual(expected.body, data["body"])
            self._assert_dates(expected.publish_date, data["publish_date"])

        # import ipdb;
        # ipdb.sset_trace()

    def test_get_empty_list_when_post_has_no_comments(self):
        for post in self.posts[1:2]:
            path = reverse("api_v1:post_comments", args=(post.slug,))
            response = self.client.get(path)
            json = response.json()
            self.assertEqual(0, len(json))
            self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_404_when_request_not_existing_post(self):
        path = reverse("api_v1:post_comments", args=("testtest",))
        response = self.client.get(path)

        json = response.json()
        expected_json = {"detail": "Not found."}
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_json, json)

    def test_404_when_request_unpublished_posts(self):
        for post in self.unpublished_posts:
            path = reverse("api_v1:post_comments", args=(post.slug,))
            response = self.client.get(path)
            json = response.json()
            expected_json = {"detail": "Not found."}
            self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
            self.assertEqual(expected_json, json)

#     def test_add_comment_to_post(self):
#         path = reverse("api_v1:post_comments", args=(self.post_1.slug,))
#
#
#     def test_added_comment_is_not_publish(self):
#         pass
# #
#     def test_400_when_sent_comment_with_invalid_data(self):
#         pass
