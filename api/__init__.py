from flasgger import LazyJSONEncoder
from flask import Flask

from config import SWAGGERUI_BLUEPRINT, SWAGGER_URL


# Routes


def init_app(config):
    app = Flask(__name__)
    # Configuration
    app.config.from_object(config)
    app.json_encoder = LazyJSONEncoder

    # Swagger
    # app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    # ----- BLUEPRINTS --------
    from api.routes import Votes, Posts
    app.register_blueprint(Votes.votes, url_prefix='/votes')
    app.register_blueprint(Posts.posts, url_prefix='/posts')
    return app
