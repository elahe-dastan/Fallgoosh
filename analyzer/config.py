import os

RABBIT_MQ_URI = os.getenv('RABBIT_MQ_URI', 'localhost')
RABBIT_MQ_QUEUE = os.getenv('RABBIT_MQ_QUEUE', 'tweet-stream')
SVM = os.getenv('SVM', './finalized_model.sav')

SKIPPED_WORD_LEN = os.getenv('SKIPPED_WORD_LEN', 3)
