import random
import string
import traceback
from http import HTTPStatus

import mariadb
from flask import Blueprint, jsonify, request

from api.models.PermissionModel import PermissionName, PermissionType


from api.models.PostModel import Post, PostType
from api.services.PostService import PostService
from api.utils.AppExceptions import EmptyDbException, NotFoundException, handle_maria_db_exception, BadRequestException
from api.utils.FirebaseFunctions import readFirebase, uploadFirebase, deleteFirebase
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters
from api.utils.RandomFileName import generateRandomFileName
from api.utils.Security import Security


posts = Blueprint('posts_blueprint', __name__)


@posts.route('/', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.VOTES_MANAGER, PermissionType.READ)])
def get_all_posts(*args):
    try:
        params = QueryParameters(request)
        posts_list = PostService.get_all_posts(params)
        response_posts = []
        for post in posts_list:
            path = ""
            if post.type == PostType.IMAGE:
                path = "images/posts/%s" % post.content
            elif post.type == PostType.VIDEO:
                path = "videos/posts/%s" % post.content

            post.content = readFirebase(path)
            response_posts.append(post.to_json())
        response = jsonify({'success': True, 'data': response_posts})
        return response, HTTPStatus.OK
    except mariadb.OperationalError as ex:
        response = jsonify({'success': False, 'message': str(ex)})
        return response, HTTPStatus.SERVICE_UNAVAILABLE
    except EmptyDbException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@posts.route('/<post_id>', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.READ)])
def get_post_by_id(*args, post_id):
    try:
        post_id = int(post_id)
        post = PostService.get_post_by_id(post_id)
        path = ""
        if post.type == PostType.IMAGE:
            path = "images/posts/%s" % post.content
        elif post.type == PostType.VIDEO:
            path = "videos/posts/%s" % post.content
        post.content = readFirebase(path)
        response = jsonify({'success': True, 'data': post.to_json()})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError:
        return jsonify({'message': "Post id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@posts.route('/', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.VOTES_MANAGER, PermissionType.WRITE)])
def add_post(*args):
    try:
        user_id = int(request.form['user'])
        topic_id = int(request.form['topic'])
        title = request.form['title']
        post_type = PostType(int(request.form['type']))
        content = request.files['content']
        visible = request.form['visible']
        content_name = generateRandomFileName(content)
        _post = Post(postId=0, userId=user_id, topicId=topic_id, title=title, post_type=post_type, content=content_name, visible=visible)
        PostService.add_post(_post)
        path = ""
        if post_type == PostType.IMAGE:
            path = "images/posts/%s" % content_name
        elif post_type == PostType.VIDEO:
            path = "videos/posts/%s" % content_name

        uploadFirebase(image=content, path=path, content_type=post_type)
        response = jsonify({'message': 'Post created successfully', 'success': True, 'post': _post.to_json()})
        return response, HTTPStatus.OK
    except KeyError as ex:
        Logger.add_to_log("error", str(ex))
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except mariadb.IntegrityError as ex:
        response = handle_maria_db_exception(ex)
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@posts.route('/<post_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.WRITE)])
def delete_post(*args, post_id):
    try:
        post_to_delete = PostService.get_post_by_id(post_id)
        response_message = PostService.delete_post(post_id)
        path = ""
        if post_to_delete.type == PostType.IMAGE:
            path = "images/posts/%s" % post_to_delete.content
        elif post_to_delete.type == PostType.VIDEO:
            path = "videos/posts/%s" % post_to_delete.content

        deleteFirebase(path)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@posts.route('/<post_id>', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.WRITE)])
def edit_post(*args, post_id):
    try:

        user_id = int(request.form['user'])
        topic_id = int(request.form['topic'])
        title = request.form['title']
        post_type = PostType(int(request.form['type']))
        visible = request.form['visible']
        # GET OLD POST
        old_post = PostService.get_post_by_id(post_id)
        Logger.add_to_log("info", old_post.to_json())
        content_name = old_post.content
        if len(request.files) <= 0 and post_type != old_post.type:
            raise BadRequestException("New type was specified but no file was provided")
        if len(request.files) > 0:
            # IF EDIT FILES EXISTS IN REQUEST
            content = request.files['content']
            Logger.add_to_log("info", "uploading files to firebase")
            content_name = generateRandomFileName(request.files['content'])
            path = ""
            old_path = ""
            # UPLOAD NEW CONTENT
            if post_type == PostType.IMAGE:
                path = "images/posts/%s" % content_name
            elif post_type == PostType.VIDEO:
                path = "videos/posts/%s" % content_name
            uploadFirebase(image=content, path=path, content_type=post_type)

            # DELETE OLD CONTENT
            if old_post.type == PostType.IMAGE:
                old_path = "images/posts/%s" % old_post.content
            elif old_post.type == PostType.VIDEO:
                old_path = "videos/posts/%s" % old_post.content
            deleteFirebase(old_path)

        _post = Post(postId=post_id, userId=user_id, topicId=topic_id, title=title, post_type=post_type,
                     content=content_name, visible=visible)
        response_message = PostService.update_post(_post)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except BadRequestException as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except KeyError as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except mariadb.IntegrityError as ex:
        response = handle_maria_db_exception(ex)
        return response, HTTPStatus.BAD_REQUEST
    except NotFoundException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR
