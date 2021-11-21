import logging
from app import app

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s : %('
                                                                       f'message)s')
logger = logging.getLogger(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

if __name__ == '__main__':
    logger.debug("Server Running..")
    app.run(debug=True)
