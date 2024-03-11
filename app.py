from api import init_app
from config import my_config

configuration = my_config['development']
app = init_app(configuration)

if __name__ == "__main__":
    app.run(port=8084)
