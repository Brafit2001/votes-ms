

class Reel:

    def __init__(self,reelId,userId, topicId, title, image, video):
        self.reelId = reelId
        self.userId = userId
        self.topicId = topicId
        self.title = title
        self.image = image
        self.video = video

    def to_json(self):
        return {
            'reelId': self.reelId,
            'userId': self.userId,
            'topicId': self.topicId,
            'title': self.title,
            'image': self.image,
            'video': self.video,
        }


def row_to_reel(row):
    return Reel(
        reelId=row[0],
        userId=row[1],
        topicId=row[2],
        title=row[3],
        image=row[4],
        video=row[5]
    )
