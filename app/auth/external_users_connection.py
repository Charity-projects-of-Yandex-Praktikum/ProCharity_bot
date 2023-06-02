from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import Schema, fields
from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.logger import app_logger as logger
from app.models import User


class UserConnectionSchema(Schema):
    telegram_id = fields.Integer(required=True)
    external_id = fields.Integer(required=True)


class ExternalUserConnection(Resource, MethodResource):

    @doc(description='Set external_id to user by his telegrma_id.'
                     'Requires "telegram_id" and "external_id" parameters.',
         summary='Set external_id to user',
         tags=['User Registration'],
         responses={
             200: {'description': 'external_id has been assigned to the user'},
             400: {'description': 'The telegram_id can not be empty'},
         },
         params={
             'telegram_id': {
                 'description': (
                    'Set external_id to a user with that telegram id'
                  ),
                 'in': 'query',
                 'type': 'integer',
                 'required': True
             },
             'external_id': {
                 'description': (
                    'Set that external_id to user.'
                  ),
                 'in': 'query',
                 'type': 'integer',
                 'required': True
             },
             'Authorization': config.PARAM_HEADER_AUTH,
         }
         )
    @use_kwargs(UserConnectionSchema)
    @jwt_required()
    def post(self, **kwargs):
        telegram_id = kwargs.get('telegram_id')
        external_id = kwargs.get('external_id')

        if not external_id or not telegram_id:
            logger.info(
                'Messages: The <telegram_id> and <external_id>  '
                'parameters have not been passed'
                )
            return make_response(
                jsonify(
                    result=(
                        'Необходимо указать параметры '
                        '<telegram_id> and <external_id>.'
                    )
                ), 400
                )

        try:
            user = User.query.filter_by(telegram_id=telegram_id).first()
            user.external_id = external_id
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Messages: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(
                jsonify(message=f'Bad request: {str(ex)}'), 400
            )

        logger.info(
            f'External user registration: The user with "{telegram_id}" '
            f'was successfully assigned the external_id "{external_id}".'
        )

        return make_response(
            jsonify(
                result="Пользователю успешно присвоен external_id."
            ), 200
        )
