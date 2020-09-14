#! -*- coding: utf-8 -*-

from os import environ
import boto3

from .errors import ParameterException


class ConnectionManager:

    def __init__(self, mode=None, config=None, endpoint=None,
                 port=None, use_instance_metadata=False):
        self.db = None
        if mode == "local":
            if config is not None:
                raise ParameterException('Cannot specify config when in local mode')
            endpoint = endpoint or 'localhost'
            port = port or '8000'
            self.db = self.getDynamoDBConnection(
                endpoint=endpoint, port=port, local=True)
        elif mode == "service":
            self.db = self.getDynamoDBConnection(
                config=config,
                endpoint=endpoint,
                use_instance_metadata=use_instance_metadata)
        else:
            raise ParameterException("Invalid arguments, please refer to usage.")

    def getDynamoDBConnection(self, config=None, endpoint=None, port=None,
                              local=False, use_instance_metadata=False):
        if not config:
            config = {'region_name': 'us-west-2'}
        params = {
            'region_name': config.get('region_name', 'cn-north-1')
        }
        if local:
            endpoint_url = 'http://{endpoint}:{port}'.format(endpoint=endpoint,
                                                             port=port)
            params['endpoint_url'] = endpoint_url
            db = boto3.resource('dynamodb', **params)
        else:
            if not config or not isinstance(config, dict):
                raise ParameterException("Invalid config")
            params.update(config)
            db = boto3.resource('dynamodb', **params)
            db.meta.client.meta.config.connect_timeout = environ.get(
                'DYNAMODB_CONNECT_TIMEOUT', 1)
            db.meta.client.meta.config.read_timeout = environ.get(
                'DYNAMODB_READ_TIMEOUT', 2)
        return db


config = {
    'aws_access_key_id': environ.get('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': environ.get('AWS_SECRET_ACCESS_KEY'),
    'region_name': environ.get('AWS_DEFAULT_REGION', 'ap-east-1')
}

db = ConnectionManager(mode='service', config=config).db
#if environ.get('DEBUG') is not '1':
#    db = ConnectionManager(mode='service', config=config).db
#else:
#    dev_endpoint = environ.get('DEV_END', 'localhost')
#    db = ConnectionManager(mode='local', endpoint=dev_endpoint).db
