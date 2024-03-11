class QueryParameters:

    def __init__(self, request):
        self.user = request.args.get("user")
        self.topic = request.args.get("topic")
        self.reel = request.args.get("reel")

    def add_to_query(self, query: str):
        for param in self.__dict__:
            param_value = getattr(self, param)
            if param_value is not None:

                if "where" not in query:
                    query += f" where {param} in ({param_value})"
                else:
                    query += f" and {param} in ({param_value})"
        return query
