from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from blog_app.blog.factories import PostFactory
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
        for expected, received in zip(expected_data, received_data):
            self.assertEqual(expected.slug, received["slug"])
            self.assertEqual(expected.title, received["title"])
            self.assertEqual(expected.summary, received["summary"])
            self._assert_dates(expected.publish_date, received["publish_date"])
            # self.assertEqual((expected.publish_date + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S"), received["publish_date"])

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
    def _create_unpublished_posts(self):
        return (
            self._create_posts_with_past_publish_date_and_with_status_draft(1)
            + self._create_posts_with_future_publish_date_and_status_published(1)
            + self._create_posts_with_future_publish_date_and_status_draft(1)
        )

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


# class CommentsListTest(APITestCase):
#     def test_get_post_comments(self):
#         pass
#
#     def test_get_empty_list_when_post_has_no_comments(self):
#         pass
#
#     def test_404_when_request_not_existing_post(self):
#         pass
#
#     def test_404_when_request_unpublished_posts(self):
#         pass
#
#     def test_insert_comment_to_post(self):
#         pass
#
#     def test_400_when_sent_comment_with_invalid_data(self):
#         pass
