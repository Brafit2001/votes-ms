from enum import Enum


class PostType(Enum):
    IMAGE = 0
    VIDEO = 1
    REEL = 2


class Post:

    def __init__(self, postId, userId, topicId, title, post_type: PostType, content):
        self.postId = postId
        self.userId = userId
        self.topicId = topicId
        self.title = title
        self.type = post_type
        self.content = content

    def to_json(self):
        return {
            'postId': self.postId,
            'userId': self.userId,
            'topicId': self.topicId,
            'title': self.title,
            'type': self.type.name,
            'content': self.content,
        }


def row_to_post(row):
    return Post(
        postId=row[0],
        userId=row[1],
        topicId=row[2],
        title=row[3],
        post_type=PostType(row[4]),
        content=row[5]
    )
