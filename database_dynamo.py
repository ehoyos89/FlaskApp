"""Capa de base de datos: la versión de DynamoDB"""
import uuid

import boto3

def list_employees():
    """Selecciona todos los empleados de la base de datos."""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Employees')
        return table.scan()["Items"]
    except:
        return 0

def load_employee(employee_id):
    """Selecciona un empleado de la base de datos."""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Employees')
        response = table.get_item(
            Key={
                'id': employee_id
            }
        )
        return response['Item']
    except:
        pass

def add_employee(object_key, full_name, location, job_title, badges):
    """Agrega un empleado a la base de datos."""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Employees')
        item = {
            'id': str(uuid.uuid4()),
            'full_name': full_name,
            'job_title': job_title,
            'location': location
        }
        if object_key:
            item['object_key'] = object_key
        if badges:
            item['badges'] = badges.split(',')

        table.put_item(
            Item=item
        )
    except:
        pass


def update_employee(employee_id, object_key, full_name, location, job_title, badges):
    """Actualiza un empleado en la base de datos."""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Employees')
        item = {
            'full_name': {'Value': full_name, 'Action': 'PUT'},
            'job_title': {'Value': job_title, 'Action': 'PUT'},
            'location': {'Value': location, 'Action': 'PUT'}
        }
        if object_key:
            item['object_key'] = {'Value': object_key, 'Action': 'PUT'}
        if badges:
            item['badges'] = {'Value': badges.split(','), 'Action': 'PUT'}
        else:
            item['badges'] = {'Action': 'DELETE'}

        table.update_item(
            Key={
                'id': employee_id
            },
            AttributeUpdates=item
        )
    except:
        pass

def delete_employee(employee_id):
    """Elimina un empleado."""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Employees')
        table.delete_item(
            Key={
                'id': employee_id
            }
        )
    except:
        pass
