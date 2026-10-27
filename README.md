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

Will build client application first as this does not contain any business logic and
will be simpler to implement

# Limitations

This system does not perform any actual cancellations and only provides the user with informaion about whether their order can be
cancelled. 
This system also makes no attempt to verify who the user is and therefore a malicious user could gain access to information about
other customers orders.
The user message is also never given to the LLM just the policy decision which is determined by code on the server. 
This means that the messages cannot be personalised and limits the scope of what the LLM can do in this system, but this also makes the system more resilient to prompt injection attacks.
This approach would also struggle to scale to larger amounts of queries as this approach is limited to one machine running the server.

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
export DOPPLER_TOKEN="dp.st.prd.xxxx"
```

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



