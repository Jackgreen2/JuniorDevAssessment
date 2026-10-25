"""CLI client. No LLM credentials are needed here."""
import sys

import requests


def read_message():
    if len(sys.argv) > 1:
        return ' '.join(sys.argv[1:])
    return input('Customer message: ')


def request_draft(message):
    response = requests.post(
        'http://127.0.0.1:5000/draft', json={'message': message}, timeout=40,
    )
    return response, response.json()


def display_response(response, body):
    if not response.ok:
        print(body.get('error', 'The server could not process the message.'), file=sys.stderr)
        return 1
    print('Draft response:')
    print(body['draft'])
    return 0


def main():
    try:
        message = read_message()
        response, body = request_draft(message)
    except (EOFError, KeyboardInterrupt):
        print('\nExiting.')
        return 0
    except requests.RequestException:
        print('Could not get a response. Check that the server is running.', file=sys.stderr)
        return 1
    return display_response(response, body)


if __name__ == '__main__':
    sys.exit(main())
