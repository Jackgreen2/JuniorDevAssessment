import os
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import server


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('server.draft_reply', return_value='A draft. No cancellation has been made.')
    def test_policy_and_read_only_data(self, llm):
        original = server.ORDERS_PATH.read_bytes()
        for order_id, allowed in [('ORD-1001', True), ('ORD-1002', False)]:
            response = self.client.post('/draft', json={'message': f'Cancel {order_id.lower()}'})
            self.assertEqual(response.status_code, 200)
            order, decision = llm.call_args.args
            self.assertEqual(order['id'], order_id)
            self.assertIn('is allowed' if allowed else 'is not allowed', decision)
        self.assertEqual(original, server.ORDERS_PATH.read_bytes())

    @patch('server.draft_reply')
    def test_missing_and_unknown_ids_skip_llm(self, llm):
        for message, expected in [('Cancel my order', 'provide your order ID'),
                                  ('Cancel ORD-9999', "couldn't find")]:
            response = self.client.post('/draft', json={'message': message})
            self.assertEqual(response.status_code, 200)
            self.assertIn(expected, response.json['draft'])
        llm.assert_not_called()

    def test_invalid_input(self):
        for body in [None, [], {}, {'message': 3}, {'message': '   '}]:
            self.assertEqual(self.client.post('/draft', json=body).status_code, 400)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self):
        self.assertEqual(self.client.post('/draft', json={'message': 'ORD-1001'}).status_code, 503)

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('server.draft_reply', side_effect=ValueError('Empty response'))
    def test_llm_failure(self, llm):
        response = self.client.post('/draft', json={'message': 'ORD-1001'})
        self.assertEqual(response.status_code, 502)
        self.assertIn('error', response.json)

    @patch('server.Anthropic')
    def test_model_receives_decision_and_draft_only_instruction(self, sdk):
        sdk.return_value.messages.create.return_value.content = [
            SimpleNamespace(type='text', text='A draft'),
        ]
        self.assertEqual(server.draft_reply({'id': 'ORD-1001'}, 'allowed'), 'A draft')
        arguments = sdk.return_value.messages.create.call_args.kwargs
        self.assertIn('no cancellation has been made', arguments['system'])
        self.assertIn('allowed', arguments['messages'][0]['content'])


if __name__ == '__main__':
    unittest.main()
