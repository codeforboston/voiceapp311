import logging
import argparse

logger = logging.getLogger('mycity')
logger.setLevel(logging.INFO) # Must be changed for debug/verbose
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
