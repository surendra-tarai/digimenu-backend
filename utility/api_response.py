'''
    Generate REST API response in common file to maitain standard response
    accross all API calls
'''

from utility import Logger
LOGGER = Logger('DAL')


def make_response(status_code: int, message: str = '', data: dict = None, errors: list = [], pagination: dict = None):
    '''
        Build API response based on given status code, message, data.

        Parameters:
        status_code (int): HTTP status code
        message (str): Small descriptive message about API resposne
        data (any): API response data like entity list, details, operation status, etc.

        Returns:
        dict: {'message': <descriptive message>, 'data': <response data>}
    '''
    if not isinstance(status_code, int) or status_code not in range(100, 600):
        status_code = 500
        LOGGER.critical(
            f'Wrong status code {status_code} supplied with message: {message} and data: {data}')
    message = str(message)

    if 200 <= status_code <= 299:
        message = message or 'Ok'
    elif status_code == 400:
        message = message or 'Bad request.'
    elif status_code == 401:
        message = message or 'Invalid authorization token.'
    elif status_code == 404:
        message = message or 'Resource deleted or not found.'
    elif status_code == 500:
        message = message or 'Internal server error.'
    elif status_code == 501:
        message = message or 'Service is not implemented yet.'

    response_data = {'message': message}

    if status_code in range(400, 600) and errors:
        response_data['errors'] = errors
    elif status_code in range(200, 300):
        if data:
            response_data['data'] = data
        if pagination:
            response_data['pagination'] = pagination

    return response_data, status_code