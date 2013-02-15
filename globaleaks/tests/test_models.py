from twisted.internet.defer import inlineCallbacks

from globaleaks.db import createTables
from globaleaks.models import *
from globaleaks.settings import transact
from globaleaks.tests import helpers

class TestModels(helpers.TestGL):
    def setUp(self):
        helpers.TestGL.setUp(self)
        return self._setup_database()

    @transact
    def _setup_database(self, store):
        createTables(True)

    @transact
    def context_add(self, store):
        context = Context(self.dummyContext)
        store.add(context)
        return context.id

    @transact
    def context_get(self, store, context_id):
        context = store.find(Context, Context.id == context_id).one()
        if context is None:
            return None
        return context.id

    @transact
    def context_del(self, store, context_id):
        context = store.find(Context, Context.id == context_id).one()
        if context is not None:
            store.remove(context)

    @transact
    def receiver_add(self, store):
        receiver = Receiver(self.dummyReceiver)
        store.add(receiver)
        return receiver.id

    @transact
    def receiver_get(self, store, receiver_id):
        receiver = store.find(Receiver, Receiver.id == receiver_id).one()
        if receiver is None:
            return None
        return receiver.id

    @transact
    def receiver_del(self, store, receiver_id):
        receiver = store.find(Receiver, Receiver.id == receiver_id).one()
        if receiver is not None:
            store.remove(receiver)

    @transact
    def create_context_with_receivers(self, store):
        context = Context(self.dummyContext)
        receiver1 = Receiver(self.dummyReceiver)
        receiver2 = Receiver(self.dummyReceiver)
        context.receivers.add(receiver1)
        context.receivers.add(receiver2)
        store.add(context)
        return context.id

    @transact
    def create_receiver_with_contexts(self, store):
        receiver = Receiver(self.dummyReceiver)
        context1 = Context(self.dummyContext)
        context2 = Context(self.dummyContext)
        receiver.contexts.add(context1)
        receiver.contexts.add(context2)
        store.add(receiver)
        return receiver.id

    @transact
    def list_receivers_of_context(self, store, context_id):
        context = store.find(Context, Context.id == context_id).one()
        receivers = []
        for receiver in context.receivers:
            receivers.append(receiver.id)
        return receivers

    @transact
    def list_context_of_receivers(self, store, receiver_id):
        receiver = store.find(Receiver, Receiver.id == receiver_id).one()
        contexts = []
        for context in receiver.contexts:
            contexts.append(context.id)
        return contexts

    @inlineCallbacks
    def test_1_context_add_and_get(self):
        context_id = yield self.context_add()
        context_id = yield self.context_get(context_id)
        self.assertIsNotNone(context_id)

    @inlineCallbacks
    def test_2_context_add_and_del(self):
        context_id = yield self.context_add()
        yield self.context_del(context_id)
        context_id = yield self.context_get(context_id)
        self.assertIsNone(context_id)

    @inlineCallbacks
    def test_3_receiver_add_and_get(self):
        receiver_id = yield self.receiver_add()
        receiver_id = yield self.receiver_get(receiver_id)
        self.assertIsNotNone(receiver_id)

    @inlineCallbacks
    def test_4_receiver_add_and_del(self):
        receiver_id = yield self.receiver_add()
        yield self.receiver_del(receiver_id)
        receiver_id = yield self.receiver_get(receiver_id)
        self.assertIsNone(receiver_id)

    @inlineCallbacks
    def test_5_context_receiver_reference_1(self):
        context_id = yield self.create_context_with_receivers()
        receivers = yield self.list_receivers_of_context(context_id)
        self.assertEqual(2, len(receivers))

    @inlineCallbacks
    def test_5_context_receiver_reference_2(self):
        receiver_id = yield self.create_receiver_with_contexts()
        contexts = yield self.list_context_of_receivers(receiver_id)
        self.assertEqual(2, len(contexts))
