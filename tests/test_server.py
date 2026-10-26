"""Check server behaviour without making paid Anthropic calls."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import server


class DraftTests(unittest.TestCase):
    # Create a fresh Flask client with a fake API key for each test.
    def setUp(self):
        self.client = server.app.test_client()
        environment = patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
        environment.start()
        self.addCleanup(environment.stop)

    # Check processing and shipped orders use the correct policy without changing data.
    @patch('server.draft_reply', return_value='No cancellation has been made.')
    def test_policy_and_read_only_data(self, mock_draft_reply):
        original_data = server.ORDERS_PATH.read_bytes()
        cases = [
            ('ORD-101', 'Cancellation is allowed'),
            ('ORD-102', 'Cancellation is not allowed'),
        ]

        for order_id, expected_decision in cases:
            with self.subTest(order_id=order_id):
                response = self.client.post(
                    '/draft', json={'message': f'Cancel {order_id.lower()}'},
                )

                self.assertEqual(response.status_code, 200)
                order, decision = mock_draft_reply.call_args.args
                self.assertEqual(order['order_id'], order_id)
                self.assertIn(expected_decision, decision)
                self.assertEqual(response.json['draft'], 'No cancellation has been made.')

        self.assertEqual(server.ORDERS_PATH.read_bytes(), original_data)

    # Ask for a missing order ID without calling the model.
    @patch('server.draft_reply')
    def test_missing_order_id(self, mock_draft_reply):
        response = self.client.post('/draft', json={'message': 'Cancel my order'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('provide your order ID', response.json['draft'])
        mock_draft_reply.assert_not_called()

    # Report an unknown order without calling the model.
    @patch('server.draft_reply')
    def test_unknown_order_id(self, mock_draft_reply):
        response = self.client.post('/draft', json={'message': 'Cancel ORD-9999'})

        self.assertEqual(response.status_code, 200)
        self.assertIn("couldn't find", response.json['draft'])
        mock_draft_reply.assert_not_called()

    # Reject missing, invalid, or blank message values.
    def test_invalid_input(self):
        invalid_bodies = [None, [], {}, {'message': 3}, {'message': '   '}]

        for body in invalid_bodies:
            with self.subTest(body=body):
                response = self.client.post('/draft', json=body)

                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json)

    # Return a configuration error when the API key is missing.
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''})
    def test_missing_key(self):
        response = self.client.post('/draft', json={'message': 'ORD-101'})

        self.assertEqual(response.status_code, 503)
        self.assertIn('error', response.json)

    # Return an error when the model cannot produce a draft.
    @patch('server.draft_reply', side_effect=ValueError('Empty response'))
    def test_llm_failure(self, mock_draft_reply):
        response = self.client.post('/draft', json={'message': 'ORD-101'})

        self.assertEqual(response.status_code, 502)
        self.assertIn('error', response.json)

    # Send the policy decision and draft-only instructions to Anthropic.
    @patch('server.Anthropic')
    def test_model_receives_decision_and_draft_only_instruction(self, mock_anthropic):
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value.content = [
            SimpleNamespace(type='text', text='A draft'),
        ]
        order = {'order_id': 'ORD-101'}

        reply = server.draft_reply(order, 'allowed')

        self.assertEqual(reply, 'A draft')
        request_arguments = mock_client.messages.create.call_args.kwargs
        self.assertIn('no cancellation has been made', request_arguments['system'])
        self.assertIn('allowed', request_arguments['messages'][0]['content'])


if __name__ == '__main__':
    unittest.main()
