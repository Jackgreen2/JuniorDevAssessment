import os
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import server


class DraftTests(unittest.TestCase):
    # Create a Flask test client before each test.
    def setUp(self):
        self.client = server.app.test_client()

    # Check both policy outcomes and confirm order data remains unchanged.
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('server.draft_reply', return_value='A draft. No cancellation has been made.')
    def test_policy_and_read_only_data(self, llm):
        original = server.ORDERS_PATH.read_bytes()
        for order_id, allowed in [('ORD-101', True), ('ORD-102', False)]:
            response = self.client.post('/draft', json={'message': f'Cancel {order_id.lower()}'})
            self.assertEqual(response.status_code, 200)
            order, decision = llm.call_args.args
            self.assertEqual(order['order_id'], order_id)
            self.assertIn('is allowed' if allowed else 'is not allowed', decision)
        self.assertEqual(original, server.ORDERS_PATH.read_bytes())

    # Check missing and unknown IDs receive replies without calling the model.
    @patch('server.draft_reply')
    def test_missing_and_unknown_ids_skip_llm(self, llm):
        for message, expected in [('Cancel my order', 'provide your order ID'),
                                  ('Cancel ORD-9999', "couldn't find")]:
            response = self.client.post('/draft', json={'message': message})
            self.assertEqual(response.status_code, 200)
            self.assertIn(expected, response.json['draft'])
        llm.assert_not_called()

    # Check invalid request bodies return a validation error.
    def test_invalid_input(self):
        for body in [None, [], {}, {'message': 3}, {'message': '   '}]:
            self.assertEqual(self.client.post('/draft', json=body).status_code, 400)

    # Check a missing API key produces a service unavailable response.
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self):
        self.assertEqual(self.client.post('/draft', json={'message': 'ORD-101'}).status_code, 503)

    # Check a model failure returns a helpful error response.
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('server.draft_reply', side_effect=ValueError('Empty response'))
    def test_llm_failure(self, llm):
        response = self.client.post('/draft', json={'message': 'ORD-101'})
        self.assertEqual(response.status_code, 502)
        self.assertIn('error', response.json)

    # Check the model receives the policy decision and draft-only instructions.
    @patch('server.Anthropic')
    def test_model_receives_decision_and_draft_only_instruction(self, sdk):
        sdk.return_value.messages.create.return_value.content = [
            SimpleNamespace(type='text', text='A draft'),
        ]
        self.assertEqual(server.draft_reply({'order_id': 'ORD-101'}, 'allowed'), 'A draft')
        arguments = sdk.return_value.messages.create.call_args.kwargs
        self.assertIn('no cancellation has been made', arguments['system'])
        self.assertIn('allowed', arguments['messages'][0]['content'])


if __name__ == '__main__':
    unittest.main()
