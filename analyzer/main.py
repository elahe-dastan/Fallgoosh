from flask import Flask, request
from prometheus_client import start_http_server, Summary, Counter, Gauge, Histogram, Info, Enum, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time, random, pika, config, json, threading, os
from core import SVM
import cleaner

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
Status_Metric = Counter('sentiment_classes', 'Whether the opinion is positive or negative', ['prediction', 'category'])
tweet_stream_metrics = Counter('tweet_stream_metrics', 'Whether the tweet is skipped or not', ['skipped'])

TextCleaner = cleaner.PersianTextCleaner('stopwords.txt')
sentiment_classifier = SVM()

categories = {
    'ride_price': [
        'قیمت',
        'تومن',
        'تومان',
        'وجه',
        'ریال',
        'هزینه',
        'کرایه'
    ],
    'acceptance': [
        'قبول',
        'لغو'
    ],
    'cash_request': [
        'نقدی',
        'وجه نقد',
        'پول نقد'
    ],
    'super_app': [
        'UI',
        'سوپر اپ',
        'سوپراپ',
        'یو آی'
    ],
    'down_bug': [
        'خطا'
    ],
    'driver_behaviour': [
        'راننده',
    ],
    'location_and_map': [
        'لوکیشن',
        'نقشه',
        'جی پی اس',
        'جی‌پی‌اس'
    ],
    'OTP': [
        'اس ام اس',
        'sms',
        'SMS',
        'اس‌ام‌اس',
        'پیامک',
        'کد ورود'
    ],
    'ap_wallet': [
        'درگاه پرداخت',
        'آپ',
        'آسان پرداخت'
        'کیف پول'
        'کیفه پول'
    ]
}


######################## Helpers ########################
def exist(key, doc):
    for word in categories[key]:
        if word in doc:
            return True
    return False


def tag(doc):
    labels = []
    for key in categories:
        if exist(key, doc):
            labels.append(key)

    if len(labels) == 0:
        labels = ['general']

    return labels


def predict(doc):
    doc = TextCleaner.clean(doc)
    print(" [x] Clean tweet %r" % doc)
    words = doc.split(' ')
    if len(words) < int(config.SKIPPED_WORD_LEN):
        tweet_stream_metrics.labels(skipped=1).inc()
        return "skipped"

    tweet_stream_metrics.labels(skipped=0).inc()
    prediction = sentiment_classifier.predict(doc)[0]
    labels = tag(doc)
    if prediction == 'neg':
        for label in labels:
            Status_Metric.labels(prediction='negative', category=label).inc()
    else:
        for label in labels:
            Status_Metric.labels(prediction='positive', category=label).inc()

    return prediction


def callback(ch, method, properties, body):
    parsed_body = json.loads(body.decode("utf-8"))
    tweet = parsed_body["tweet"]
    result = predict(doc=tweet)
    print(" [x] Result %r" % result)


def start_consumer():
    print(" [*] Trying to connect to  %r" % config.RABBIT_MQ_URI)
    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBIT_MQ_URI))
    print(" [*] Successfully connected to RabbitMQ  %r")
    channel = connection.channel()
    print(" [*] Start Consuming")

    channel.queue_declare(queue=config.RABBIT_MQ_QUEUE)

    channel.basic_consume(queue=config.RABBIT_MQ_QUEUE, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

Info('application_information', 'Predict the sentiment of users feedbacks from social media(currently twitter)').info({
    'version': '0.1',
})


######################## Handlers ########################
@app.route('/')
@REQUEST_TIME.time()
def index():
    return 'SnappBrain! is loading....'


@app.route('/predict', methods=['POST'])
def predict_handler():
    doc = request.form.get('doc')
    return predict(doc=doc)


consumer_thread = threading.Thread(target=start_consumer)
consumer_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
