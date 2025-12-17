import logging
import sys


logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                     level=logging.WARNING, stream=sys.stdout)

logger = logging.getLogger(__name__)