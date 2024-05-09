import traceback
from http import HTTPStatus

import mariadb
from flask import Blueprint, jsonify, request

from api.models.PermissionModel import PermissionName, PermissionType


from api.models.VoteModel import Vote
from api.services.VoteService import VoteService
from api.utils.AppExceptions import EmptyDbException, NotFoundException, handle_maria_db_exception
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters
from api.utils.Security import Security

votes = Blueprint('votes_blueprint', __name__)


@votes.route('/', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.VOTES_MANAGER, PermissionType.READ)])
def get_all_votes(*args):
    try:
        params = QueryParameters(request)
        votes_list = VoteService.get_all_votes(params)
        response_votes = []
        for vote in votes_list:
            response_votes.append(vote.to_json())
        response = jsonify({'success': True, 'data': response_votes})
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


@votes.route('/<vote_id>', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.READ)])
def get_vote_by_id(*args, vote_id):
    try:
        vote_id = int(vote_id)
        vote = VoteService.get_vote_by_id(vote_id)
        response = jsonify({'success': True, 'data': vote.to_json()})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError:
        return jsonify({'message': "Vote id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@votes.route('/', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.WRITE)])
def add_vote(*args):
    try:
        user_id = int(args[0]["userId"])
        topic_id = int(request.json['topic'])
        post_id = int(request.json['post'])
        content = float(request.json['content'])
        originality = float(request.json['originality'])
        clarity = float(request.json['clarity'])
        mean = (content + originality + clarity) / 3
        _vote = Vote(voteId=0, userId=user_id, topicId=topic_id, postId=post_id,
                     content=content, originality=originality,
                     clarity=clarity, mean=mean)
        VoteService.add_vote(_vote)
        response = jsonify({'message': 'Vote created successfully', 'success': True})
        return response, HTTPStatus.OK
    except KeyError as ex:
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


@votes.route('/<vote_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.WRITE)])
def delete_vote(*args, vote_id):
    try:
        response_message = VoteService.delete_vote(vote_id)
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


@votes.route('/<vote_id>', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.GROUPS_MANAGER, PermissionType.WRITE)])
def edit_vote(*args,vote_id):
    try:
        user_id = int(args[0]["userId"])
        topic_id = int(request.json['topic'])
        post_id = int(request.json['post'])
        content = float(request.json['content'])
        originality = float(request.json['originality'])
        clarity = float(request.json['clarity'])
        mean = (content + originality + clarity) / 3
        _vote = Vote(voteId=vote_id, userId=user_id, topicId=topic_id, postId=post_id,
                     content=content, originality=originality,
                     clarity=clarity, mean=mean)
        response_message = VoteService.update_vote(_vote)
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
