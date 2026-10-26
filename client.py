"""CLI client. No LLM credentials are needed here."""
import sys

import requests


# Read the customer message from arguments or an interactive prompt.
def read_message():
    if len(sys.argv) > 1:
        return ' '.join(sys.argv[1:])
    return input('Customer message: ')


# Send the message to Flask and decode its JSON response.
def request_draft(message):
    response = requests.post(
        'http://127.0.0.1:5000/draft', json={'message': message}, timeout=40,
    )
    return response, response.json()


# Print the draft or error and return the appropriate exit code.
def display_response(response, body):
    if not response.ok:
        print(body.get('error', 'The server could not process the message.'), file=sys.stderr)
        return 1
    print('Draft response:')
    print(body['draft'])
    return 0


# Run the client and handle input or connection failures.
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
