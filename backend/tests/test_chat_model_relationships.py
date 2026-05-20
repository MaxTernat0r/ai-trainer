from unittest import TestCase

from app.models.chat import ChatConversation


class ChatModelRelationshipsTest(TestCase):
    def test_conversation_deletes_messages_with_cascade(self):
        self.assertIn("delete", ChatConversation.messages.property.cascade)
        self.assertIn("delete-orphan", ChatConversation.messages.property.cascade)
