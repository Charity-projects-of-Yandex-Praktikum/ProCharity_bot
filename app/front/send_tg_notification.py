import datetime

from flask import jsonify, make_response, request
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.logger import app_logger as logger
from app.models import Notification
from app.request_models.telegram_notification import TelegramNotificationRequest
from app.webhooks.check_request import request_to_context
from app.webhooks.check_webhooks_token import check_webhooks_token

from bot.messages import TelegramNotification
from core.services.mailing_type import MailingType


class SendTelegramNotification(Resource, MethodResource):
    method_decorators = {'post': [check_webhooks_token]}

    @doc(description='Sends message to the Telegram chat. Requires "message" parameter.'
                     ' Messages can be sent either to subscribed users or not.To do this,'
                     ' specify the "has_mailing" parameter.Default value "True".',
         summary='Send messages to the bot chat',
         tags=['Messages'],
         responses={
             200: {'description': 'The message has been added to a query job'},
             400: {'description': 'The message can not be empty'},
         },
         params={
             'message': {
                 'description': 'Notification message. Max len 4096',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'has_mailing': {
                 'description': ('Sending notifications to users by the type of permission to mailing.'
                                 'subscribed - user has enabled a mailing.'
                                 'unsubscribed - user has disabled a mailing.'
                                 'all - send to all users'),
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'Authorization': config.PARAM_HEADER_AUTH,  # Only if request requires authorization
         }
         )
    @jwt_required()
    def post(self):
        notifications = request_to_context(TelegramNotificationRequest, request)

        if ['message', 'has_mailing'] not in notifications:
            logger.info("Messages: The <message> and  <has_mailing> parameters have not been passed")
            return make_response(jsonify(result="Необходимо указать параметры <message> и <has_mailing>."), 400)

        authorized_user = get_jwt_identity()
        message = Notification(message=notifications['message'], sent_by=authorized_user)
        db_session.add(message)
        try:
            db_session.commit()
            job_queue = TelegramNotification()

            if not job_queue.send_notification(message=message, mailing_type=MailingType.value):
                logger.info(f"Messages: Passed invalid <mailing_type> parameter. Passed: {MailingType.value}")
                return make_response(jsonify(result=f"Неверно указан параметр <mailing_type>. "
                                                    f"Сообщение не отправлено."), 400)

            message.was_sent = True
            message.sent_date = datetime.datetime.now()
            db_session.commit()

        except SQLAlchemyError as ex:
            logger.error(f'Messages: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        logger.info(f"Messages: The message '{message.message[0:30]}...' "
                    f"has been successfully added to the mailing list.")
        return make_response(jsonify(result=f"Сообщение успешно добавлено в очередь рассылки."), 200)
