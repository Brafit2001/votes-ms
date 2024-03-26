
class Vote:

    def __init__(self, voteId, userId, topicId, postId, content, originality, clarity, mean):
        self.voteId = voteId
        self.userId = userId
        self.topicId = topicId
        self.postId = postId
        self.content = content
        self.originality = originality
        self.clarity = clarity
        self.mean = mean

    def to_json(self):
        return {
            'id': self.voteId,
            'user': self.userId,
            'topic': self.topicId,
            'post': self.postId,
            'content': self.content,
            'originality': self.originality,
            'clarity': self.clarity,
            'mean': self.mean
        }


def row_to_vote(row):
    return Vote(
        voteId=row[0],
        userId=row[1],
        postId=row[2],
        topicId=row[3],
        content=row[4],
        originality=row[5],
        clarity=row[6],
        mean=row[7]
    )
