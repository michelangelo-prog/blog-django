from datetime import timedelta

import factory
from rest_framework import status
from rest_framework.test import APITestCase

from blog_app.blog.factories import CommentFactory, PostFactory, TagFactory
from blog_app.blog.models import Post
from django.urls import reverse
from django.utils import timezone


class PostMixin:
    def _create_post(self, publish_date, status, tags):
        return PostFactory.create(
                publish_date=publish_date,
                status=status,
                tags=tags
        )


    def _create_posts_with_past_publish_date_and_status_published(
        self, number_of_posts, tags
    ):
        posts = []
        for i in range(number_of_posts):
            publish_date = timezone.now() - timedelta(days=i + 1)
            post = self._create_post(publish_date, Post.STATUS.PUBLISH, tags)
            posts.append(post)

        return posts

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

    def _assert_tags_contains_required_fields(self, tags):
        expected_fields = {"title", "slug"}
        for tag in tags:
            self.assertSetEqual(expected_fields, set(tag.keys()))

    def _assert_tags(self, expected_tags, tags):
        self.assertEqual(len(expected_tags), len(tags))
        for expected_tag in expected_tags:
            received = False
            for tag in tags:
                if expected_tag.title == tag["title"] and expected_tag.slug == tag["slug"]:
                    received = True
            self.assertTrue(received)


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
        self.post_tags = (
            TagFactory(),
            TagFactory(),
        )
        self.published_posts = self._create_posts_with_past_publish_date_and_status_published(
            self.number_of_published_posts, self.post_tags
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
        expected_fields = {"slug", "title", "summary", "publish_date", "tags"}
        for expected, received in zip(expected_data, received_data):
            self.assertSetEqual(expected_fields, set(received.keys()))
            self.assertEqual(expected.slug, received["slug"])
            self.assertEqual(expected.title, received["title"])
            self.assertEqual(expected.summary, received["summary"])
            # self._assert_dates(expected.publish_date, received["publish_date"]) TODO
            self._assert_tags_contains_required_fields(received["tags"])
            self._assert_tags(expected.tags.all(), received["tags"])

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

    def test_get_published_posts_by_tag(self):
        post_tags = (
            TagFactory(),
        )

        posts = self._create_posts_with_past_publish_date_and_status_published(
            3,
            post_tags,
        )

        response = self.client.get(reverse("api_v1:posts"), {"tag": post_tags[0].slug})
        json = response.json()

        self.assertEqual(len(posts), len(json))
        self._compare_post_list_data(posts, json)


class PostTest(PostMixin, APITestCase):
    def setUp(self) -> None:
        self.number_of_published_posts = 3
        self.post_tags = (
            TagFactory(),
            TagFactory(),
        )
        self.published_posts = self._create_posts_with_past_publish_date_and_status_published(
            self.number_of_published_posts,
            self.post_tags,
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
        # self._assert_dates(post.publish_date, json["publish_date"]) TODO
        self._assert_tags_contains_required_fields(json["tags"])
        self._assert_tags(post.tags.all(), json["tags"])

    def test_when_post_contain_another_tags(self):
        post_tags = (
            TagFactory(),
            TagFactory(),
            TagFactory(),
        )

        post = self._create_posts_with_past_publish_date_and_status_published(
            1,
            post_tags,
        )[0]

        path = reverse("api_v1:post", args=(post.slug,))
        response = self.client.get(path)
        json = response.json()

        self._assert_tags_contains_required_fields(json["tags"])
        self._assert_tags(post.tags.all(), json["tags"])

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
    def _create_comments_with_past_publish_date(
        self, post, published, number_of_comments
    ):
        return [
            CommentFactory(
                post=post,
                published=published,
                publish_date=timezone.now() - timedelta(days=i + 1),
            )
            for i in range(number_of_comments)
        ]

    def _create_comments_with_future_publish_date(
        self, post, published, number_of_comments
    ):
        return [
            CommentFactory(
                post=post,
                published=published,
                publish_date=timezone.now() + timedelta(days=i + 1),
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
        self.post_tags = (
            TagFactory(),
            TagFactory(),
        )
        self.posts = self._create_posts_with_past_publish_date_and_status_published(
            self.number_of_posts, self.post_tags
        )

        # First post
        # has three published comments and three unpublished comments
        self.post_1 = self.posts[0]
        self.number_of_post_1_published_comments = 3
        self.post_1_published_comments = self._create_comments_with_past_publish_date(
            self.post_1, True, self.number_of_post_1_published_comments
        )
        self._create_unpublished_comments(self.post_1)

        # Second post
        # has three unpublished comments
        self.post_2 = self.posts[1]
        self._create_unpublished_comments(self.post_2)

        # Third post
        # has two published comments
        self.post_3 = self.posts[2]
        self.post_3_published_comments = self._create_comments_with_past_publish_date(
            self.post_3, True, 2
        )

        # Three unpublished posts
        self.unpublished_posts = self._create_unpublished_posts()

    def _compare_comments(self, expected, received):
        expected_comment_fields = {"name", "body", "publish_date"}

        self.assertEqual(len(expected), len(received))
        for exp, rec in zip(expected, received):
            self.assertSetEqual(expected_comment_fields, set(rec.keys()))
            self.assertEqual(exp.name, rec["name"])
            self.assertEqual(exp.body, rec["body"])
            # self._assert_dates(exp.publish_date, rec["publish_date"]) TODO

    def test_get_comments_for_published_post(self):
        path = reverse("api_v1:post_comments", args=(self.post_1.slug,))
        response = self.client.get(path)
        json = response.json()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._compare_comments(self.post_1_published_comments, json)

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

    def _get_comment_data(self):
        comment = factory.build(dict, FACTORY_CLASS=CommentFactory)
        comment.pop("post")
        comment.pop("published")
        comment.pop("publish_date")
        return comment

    def test_add_comment_to_post(self):
        path = reverse("api_v1:post_comments", args=(self.post_3.slug,))
        comment_data = self._get_comment_data()
        response = self.client.post(path, data=comment_data)
        json = response.json()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        expected_fields = {
            "name",
            "body",
        }
        self.assertSetEqual(expected_fields, set(json.keys()))
        self.assertEqual(comment_data["name"], json["name"])
        self.assertEqual(comment_data["body"], json["body"])

    def test_added_comment_is_not_publish(self):
        comment_data = self._get_comment_data()
        self.client.post(
            reverse("api_v1:post_comments", args=(self.post_3.slug,)), data=comment_data
        )

        response = self.client.get(
            reverse("api_v1:post_comments", args=(self.post_3.slug,))
        )
        json = response.json()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._compare_comments(self.post_3_published_comments, json)

    def test_404_when_add_comment_to_unpublished_posts(self):
        comment_data = self._get_comment_data()

        for post in self.unpublished_posts:
            response = self.client.post(
                reverse("api_v1:post_comments", args=(post.slug,)), data=comment_data
            )
            self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_400_when_sent_comment_without_fields(self):
        fields = ("name", "email", "body")
        path = reverse("api_v1:post_comments", args=(self.post_3.slug,))
        for field in fields:
            comment_data = self._get_comment_data()
            comment_data.pop(field)
            response = self.client.post(path, data=comment_data)
            self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_400_when_sent_comment_with_incorect_email(self):
        comment_data = self._get_comment_data()
        comment_data["email"] = "test"
        path = reverse("api_v1:post_comments", args=(self.post_3.slug,))
        response = self.client.post(path, data=comment_data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
