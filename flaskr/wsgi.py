from flaskr import create_app #as application
import sys

sys.path.insert(0, 'flaskr/__init__.py')
application = create_app()