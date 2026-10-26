# Junior Developer Assessment

A small Python CLI assistant that drafts order cancellation replies. The client
sends messages to a Flask server, which reads `orders.json`, applies the policy,
and asks Anthropic to write a reply. It never changes orders or cancels them.

## Setup and run

Requires Python 3.10+, the Doppler CLI, and an Anthropic API key.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
doppler login
doppler setup
```

On Windows, activate with `.venv\Scripts\Activate.ps1` instead.
Select your Doppler project/config and add `ANTHROPIC_API_KEY` in its dashboard.
Optionally set `ANTHROPIC_MODEL` (default: `claude-haiku-4-5`).
The key stays in the server environment; never commit credentials.

Start the local server:

```sh
doppler run -- python server.py
```

In another terminal, activate the environment and run:

```sh
python client.py "Please cancel ORD-101"
```

Run `python client.py` without arguments for a prompt.
The server listens on `127.0.0.1:5000` and is intended for local use.

## Policy

Each message concerns cancellation and contains at most one ID (`ORD-` followed
by digits, case insensitive). Processing orders can be cancelled; shipped orders
cannot. Missing IDs prompt a request for one; unknown orders are reported without
inventing details. Review generated drafts before sending them to customers.

## Tests

```sh
python -m unittest discover -s tests -v
```

Tests mock Anthropic, so no API key or paid calls are needed.

Manual tests used to check LLM is correctly drafting replies.


## Initial Planning Notes

Using python because of familiarity with restAPI and Jsonify which will cover message 
handling between client and server and JSON parsing. Using python will also improve 
readability of the codebase for reviewing

Structure:
Client-Server Architecture

Message Handling:
- Client sends request to server
- Server extracts order number from the message, checks whether it exists, applies the cancellation policy. 
- Server then requests LLM to craft a message back to the user giving feedback on the result of their request.
