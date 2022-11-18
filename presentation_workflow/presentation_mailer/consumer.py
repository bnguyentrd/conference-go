import json
import pika
import django
import os
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body):
    context = json.loads(body)
    send_mail(
        "Your presentation has been approved",
        f"{context['presenter_name']}, we're informing you that your presentation {context['title']} has been approved",
        "admin@conference.go",
        [context["presenter_email"]],
        fail_silently=False,
    )


def process_rejection(ch, method, properties, body):
    context = json.loads(body)
    send_mail(
        "Your presentation has been rejected",
        f"{context['presenter_name']}, we are here to inform you that {context['title']} has been rejected",
        "admin@conference.go",
        [context["presenter_email"]],
        fail_silently=False,
    )


parameters = pika.ConnectionParameters(host="rabbitmq")
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue="presentation_approvals")
channel.basic_consume(
    queue="presentation_approvals",
    on_message_callback=process_approval,
    auto_ack=True,
)
channel.queue_declare(queue="presentation_rejections")
channel.basic_consume(
    queue="presentation_rejections",
    on_message_callback=process_rejection,
    auto_ack=True,
)
channel.start_consuming()
