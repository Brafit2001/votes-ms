import traceback
from http import HTTPStatus

import mariadb
from flask import Blueprint, jsonify, request

from api.models.PermissionModel import PermissionName, PermissionType


from api.models.PostModel import Post, PostType
from api.services.PostService import PostService
from api.utils.AppExceptions import EmptyDbException, NotFoundException, handle_maria_db_exception
from api.utils.Logger import Logger
from api.utils.Security import Security


posts = Blueprint('posts_blueprint', __name__)


@posts.route('/', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.VOTES_MANAGER, PermissionType.READ)])
def get_all_posts(*args):
    try:
        posts_list = PostService.get_all_posts()
        response_posts = []
        for post in posts_list:
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
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.WRITE)])
def add_post(*args):
    try:
        user_id = int(args[0]["userId"])
        topic_id = int(request.json['topic'])
        title = request.json['title']
        post_type = PostType(int(request.json['type']))
        content = request.json['content']
        _post = Post(postId=0, userId=user_id, topicId=topic_id, title=title, post_type=post_type, content=content)
        PostService.add_post(_post)
        response = jsonify({'message': 'Post created successfully', 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
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
        response_message = PostService.delete_post(post_id)
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
        user_id = int(args[0]["userId"])
        topic_id = int(request.json['topic'])
        title = request.json['title']
        post_type = PostType(int(request.json['type']))
        content = request.json['content']
        _post = Post(postId=post_id, userId=user_id, topicId=topic_id, title=title, post_type=post_type, content=content)
        response_message = PostService.update_post(_post)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
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
