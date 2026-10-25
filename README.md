# Junior Developer Assessment

A small Python command-line assistant that drafts cancellation replies for a
fictional online shop. It never modifies orders or performs cancellations.

## Structure

- `client.py` reads a terminal message and sends it to Flask over HTTP.
- `server.py` extracts the order ID, reads local JSON, applies the cancellation
  policy in Python, and asks an LLM to word the reply using verified facts.
- `orders.json` contains fictional orders and stays on the server.

Doppler injects the Anthropic API key into the server environment; it is never sent to the
client. Python's `json` module reads order data; Flask's `jsonify` returns HTTP
responses. No database, web interface, history, or agent framework is included.

## Setup

Requires Python 3.10+ and the Doppler CLI and an Anthropic API key with access to the selected model.
Run from this directory:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

Configure Doppler in the server terminal:

```sh
doppler login
doppler setup
```

Select your Doppler project and config. In that config, add the secret
`ANTHROPIC_API_KEY` through the Doppler dashboard. Optionally add
`ANTHROPIC_MODEL`; the default is `claude-haiku-4-5`.

Start Flask with the secrets injected into its environment:

```sh
doppler run -- python server.py
```

The Anthropic SDK reads `ANTHROPIC_API_KEY` from the environment. No Doppler SDK,
secret file, or Doppler token in application code is needed. The program does not
automatically load `.env` files. Never commit credentials.

In a second terminal, activate the virtual environment and run:

```sh
python client.py "Please cancel ORD-101"
```

Use `python client.py` without arguments for an interactive prompt.
The server listens on `127.0.0.1:5000` with debug disabled. This is a local demo;
remote hosting would require HTTPS, access controls, and a production server.

## Policy and assumptions

- Each message concerns cancellation and contains at most one order ID.
- IDs are `ORD-` followed by digits, case insensitive.
- Processing orders can be cancelled; shipped orders cannot.
- Other statuses have unknown eligibility because the policy does not cover them.
- Missing IDs and unknown orders receive factual replies without an LLM call.
- The model receives the order and Python's policy decision, not the raw customer
  message. It is instructed not to invent facts or claim cancellation occurred.
- Model wording is probabilistic: review drafts before sending them to customers.
- The server only reads order data and has no cancellation operation.
- API failures return an error rather than pretending a draft was generated.

## Checks

```sh
python -m unittest discover -s tests -v
```

Tests mock the LLM, so they need no API key and incur no API charges. They cover
processing and shipped orders, missing and unknown IDs, invalid input, missing
credentials, model failure, prompt construction, and unchanged order data.

With the server running, check real model wording manually:

```sh
python client.py "Please cancel ORD-101"
python client.py "Please cancel ORD-102"
python client.py "Please cancel my order"
python client.py "Please cancel ORD-9999"
```

Expect eligibility, ineligibility, a request for an ID, and an order-not-found
reply respectively. Generated replies must not claim a cancellation occurred.
Live model checks require a configured key and API access.
