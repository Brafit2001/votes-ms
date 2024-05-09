import traceback

import mariadb

from api.database.db import get_connection
from api.models.PostModel import Post, row_to_post
from api.utils.AppExceptions import NotFoundException, EmptyDbException
from api.utils.Logger import Logger


class PostService:

    @classmethod
    def get_all_posts(cls, params) -> list[Post]:
        try:
            connection_dbvotes = get_connection('dbvotes')
            posts_list = []
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = "select * from posts"
                query = params.add_to_query(query)
                cursor_dbvotes.execute(query)
                result_set = cursor_dbvotes.fetchall()
                if not result_set:
                    raise EmptyDbException("No posts found")
                for row in result_set:
                    post = row_to_post(row)
                    posts_list.append(post)
            connection_dbvotes.close()
            return posts_list
        except mariadb.OperationalError:
            raise
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_post_by_id(cls, postId: int) -> Post:
        try:
            connection_dbvotes = get_connection('dbvotes')
            post = None
            with connection_dbvotes.cursor() as cursor_dbvotes:
                query = "select * from posts where id = '{}'".format(postId)
                cursor_dbvotes.execute(query)
                row = cursor_dbvotes.fetchone()
                if row is not None:
                    post = row_to_post(row)
                else:
                    raise NotFoundException("Post not found")
            connection_dbvotes.close()
            return post
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def add_post(cls, post: Post):
        try:
            connection_dbvotes = get_connection('dbvotes')
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = ("insert into `posts` set user = '{}', topic = '{}', title = '{}', type = '{}', content "
                         "= '{}', visible = '{}'").format(
                    post.userId, post.topicId, post.title, post.type.value, post.content, post.visible)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return 'Post added'
        except mariadb.IntegrityError:
            # Post already exists
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def delete_post(cls, postId: int):
        try:
            # Check if post exists
            cls.get_post_by_id(postId)
            connection_dbvotes = get_connection('dbvotes')
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = "delete from `posts` where id = '{}'".format(postId)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return f'Post {postId} deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def update_post(cls, post: Post):
        try:
            # Check if post exists
            cls.get_post_by_id(post.postId)
            connection_dbvotes = get_connection('dbvotes')
            with ((connection_dbvotes.cursor()) as cursor_dbvotes):
                query = ("update `posts` set user = '{}', topic = '{}', title = '{}', type = '{}', content "
                         "= '{}', visible = '{}' where id = '{}'"
                         ).format(
                    post.userId, post.topicId, post.title, post.type.value, post.content, post.visible, post.postId)
                Logger.add_to_log("info", query)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return f'Post {post.postId} updated'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise
