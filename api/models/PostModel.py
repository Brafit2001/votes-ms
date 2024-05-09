from enum import Enum


class PostType(Enum):
    IMAGE = 0
    VIDEO = 1
    REEL = 2


class Post:

    def __init__(self, postId, userId, topicId, title, post_type: PostType, content, visible):
        self.postId = postId
        self.userId = userId
        self.topicId = topicId
        self.title = title
        self.type = post_type
        self.content = content
        self.visible = visible

    def to_json(self):
        return {
            'id': self.postId,
            'user': self.userId,
            'topic': self.topicId,
            'title': self.title,
            'type': self.type.value,
            'content': self.content,
            'visible': self.visible
        }


def row_to_post(row):
    return Post(
        postId=row[0],
        userId=row[1],
        topicId=row[2],
        title=row[3],
        post_type=PostType(row[4]),
        content=row[5],
        visible=row[6]
    )
