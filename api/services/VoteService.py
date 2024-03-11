import traceback

import mariadb

from api.database.db import get_connection
from api.models.VoteModel import Vote, row_to_vote
from api.utils.AppExceptions import NotFoundException, EmptyDbException
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters


class VoteService:

    @classmethod
    def get_all_votes(cls, params: QueryParameters) -> list[Vote]:
        try:
            connection_dbvotes = get_connection('dbvotes')
            votes_list = []
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = "select * from votes"
                query = params.add_to_query(query)
                cursor_dbvotes.execute(query)
                result_set = cursor_dbvotes.fetchall()
                if not result_set:
                    raise EmptyDbException("No votes found")
                for row in result_set:
                    vote = row_to_vote(row)
                    votes_list.append(vote)
            connection_dbvotes.close()
            return votes_list
        except mariadb.OperationalError:
            raise
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_vote_by_id(cls, voteId: int) -> Vote:
        try:
            connection_dbvotes = get_connection('dbvotes')
            vote = None
            with connection_dbvotes.cursor() as cursor_dbvotes:
                query = "select * from votes where id = '{}'".format(voteId)
                cursor_dbvotes.execute(query)
                row = cursor_dbvotes.fetchone()
                if row is not None:
                    vote = row_to_vote(row)
                else:
                    raise NotFoundException("Vote not found")
            connection_dbvotes.close()
            return vote
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def add_vote(cls, vote: Vote):
        try:
            connection_dbvotes = get_connection('dbvotes')
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = ("insert into `votes` set user = '{}', topic = '{}', reel = '{}', content = '{}', originality "
                         "= '{}', clarity = '{}', mean = '{}'").format(
                    vote.userId, vote.topicId, vote.reelId, vote.content, vote.originality, vote.clarity, vote.mean)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return 'Vote added'
        except mariadb.IntegrityError:
            # Vote already exists
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def delete_vote(cls, voteId: int):
        try:
            # Check if vote exists
            cls.get_vote_by_id(voteId)
            connection_dbvotes = get_connection('dbvotes')
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = "delete from `votes` where id = '{}'".format(voteId)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return f'Vote {voteId} deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def update_vote(cls, vote: Vote):
        try:
            # Check if vote exists
            cls.get_vote_by_id(vote.voteId)
            connection_dbvotes = get_connection('dbvotes')
            with ((connection_dbvotes.cursor()) as cursor_dbvotes):
                query = ("update `votes` set user = '{}', topic = '{}', reel = '{}', content = '{}', originality = '{}'"
                         ", clarity = '{}', mean = '{}' where id = '{}'"
                         ).format(
                    vote.userId, vote.topicId, vote.reelId, vote.content, vote.originality, vote.clarity,
                    vote.mean, vote.voteId)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return f'Vote {vote.voteId} updated'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise


