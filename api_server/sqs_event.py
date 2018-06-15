from flask import current_app
import boto3
import json

sqs = boto3.resource('sqs')


class ClusterDeployNotification(object):

    def __init__(self, cluster, payload):
        self.cluster = cluster
        self.payload = payload
        self.queue = sqs.get_queue_by_name(QueueName=current_app.config[u'AWS_SQS_NOTIFICATION_QUEUE'])
        self.callback_url = current_app.config[u'SLACK_NOTIFICATIONS_WEBHOOK_URL']

    def notify(self):
        self.queue.send_message(MessageBody=json.dumps({
            "event_type": "cluster-deploy",
            "callback_url": self.callback_url,
            "cluster": self.cluster,
            "payload": self.payload
        }))


class ServiceDestroyNotification(object):

    def __init__(self, cluster, service):
        self.cluster = cluster
        self.service = service
        self.queue = sqs.get_queue_by_name(QueueName=current_app.config[u'AWS_SQS_NOTIFICATION_QUEUE'])
        self.callback_url = current_app.config[u'SLACK_NOTIFICATIONS_WEBHOOK_URL']

    def notify(self):
        self.queue.send_message(MessageBody=json.dumps({
            "event_type": "service-destroy",
            "callback_url": self.callback_url,
            "cluster": self.cluster,
            "service": self.service
        }))
