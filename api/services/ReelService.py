import traceback

import mariadb

from api.database.db import get_connection
from api.models.ReelModel import Reel, row_to_reel
from api.utils.AppExceptions import NotFoundException, EmptyDbException
from api.utils.Logger import Logger


class ReelService:

    @classmethod
    def get_all_reels(cls) -> list[Reel]:
        try:
            connection_dbvotes = get_connection('dbvotes')
            reels_list = []
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = "select * from reels"
                cursor_dbvotes.execute(query)
                result_set = cursor_dbvotes.fetchall()
                if not result_set:
                    raise EmptyDbException("No reels found")
                for row in result_set:
                    reel = row_to_reel(row)
                    reels_list.append(reel)
            connection_dbvotes.close()
            return reels_list
        except mariadb.OperationalError:
            raise
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_reel_by_id(cls, reelId: int) -> Reel:
        try:
            connection_dbvotes = get_connection('dbvotes')
            reel = None
            with connection_dbvotes.cursor() as cursor_dbvotes:
                query = "select * from reels where id = '{}'".format(reelId)
                cursor_dbvotes.execute(query)
                row = cursor_dbvotes.fetchone()
                if row is not None:
                    reel = row_to_reel(row)
                else:
                    raise NotFoundException("Reel not found")
            connection_dbvotes.close()
            return reel
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def add_reel(cls, reel: Reel):
        try:
            connection_dbvotes = get_connection('dbvotes')
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = ("insert into `reels` set user = '{}', topic = '{}', title = '{}', image = '{}', video "
                         "= '{}'").format(
                    reel.userId, reel.topicId, reel.title, reel.image, reel.video)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return 'Reel added'
        except mariadb.IntegrityError:
            # Reel already exists
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def delete_reel(cls, reelId: int):
        try:
            # Check if reel exists
            cls.get_reel_by_id(reelId)
            connection_dbvotes = get_connection('dbvotes')
            with (connection_dbvotes.cursor()) as cursor_dbvotes:
                query = "delete from `reels` where id = '{}'".format(reelId)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return f'Reel {reelId} deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def update_reel(cls, reel: Reel):
        try:
            # Check if reel exists
            cls.get_reel_by_id(reel.reelId)
            connection_dbvotes = get_connection('dbvotes')
            with ((connection_dbvotes.cursor()) as cursor_dbvotes):
                query = ("update `reels` set user = '{}', topic = '{}', title = '{}', image = '{}', video "
                         "= '{}' where id = '{}'"
                         ).format(
                    reel.userId, reel.topicId, reel.title, reel.image, reel.video, reel.reelId)
                cursor_dbvotes.execute(query)
                connection_dbvotes.commit()
            connection_dbvotes.close()
            return f'Reel {reel.reelId} updated'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise
