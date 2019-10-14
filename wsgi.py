from gitlabjira import app as application
#print(application)
from config import Config

if __name__ == "__main__":
    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
