
class Vote:

    def __init__(self, voteId, userId, postId, mean, ratings=None):
        if ratings is None:
            ratings = {}
        self.voteId = voteId
        self.userId = userId
        self.postId = postId
        self.mean = mean
        self.ratings = ratings

    def to_json(self):
        return {
            'id': self.voteId,
            'user': self.userId,
            'post': self.postId,
            'mean': self.mean,
            'ratings': self.ratings
        }


def row_to_vote(row):
    return Vote(
        voteId=row[0],
        userId=row[1],
        postId=row[2],
        mean=row[3]
    )

