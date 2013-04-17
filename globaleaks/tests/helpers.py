import os
import json
import time
import uuid

from cyclone import httpserver
from cyclone.web import Application
from cyclone.util import ObjectDict as OD

from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.internet.defer import inlineCallbacks

from storm.twisted.testing import FakeThreadPool

from globaleaks.settings import GLSetting, transact
from globaleaks.handlers.admin import create_context, create_receiver
from globaleaks.handlers.submission import create_submission, create_whistleblower_tip
from globaleaks import db

DEFAULT_PASSWORD = u'yustapassword'
transact.tp = FakeThreadPool()
GLSetting.scheduler_threadpool = FakeThreadPool()
GLSetting.notification_plugins = []
GLSetting.sessions = {}
GLSetting.working_path = os.path.abspath(os.path.join(GLSetting.root_path, 'testing_dir'))
GLSetting.eval_paths()
GLSetting.remove_directories()

transact.debug = True
class TestWithDB(unittest.TestCase):
    def setUp(self):
        GLSetting.create_directories()
        return db.create_tables(create_node=True)

    def tearDown(self):
        GLSetting.remove_directories()

class TestGL(TestWithDB):
    @inlineCallbacks
    def _setUp(self):
        yield TestWithDB.setUp(self)
        self.setUp_dummy()
        yield self.fill_data()

    def setUp(self):
        return self._setUp()

    @inlineCallbacks
    def fill_data(self):
        try:
            self.dummyReceiver = yield create_receiver(self.dummyReceiver)
        except Exception as excp:
            print "Fail fill_data/create_receiver: %s" % excp

        try:
            self.dummyContext['receivers'] = [ self.dummyReceiver['receiver_gus'] ]
            self.dummyContext = yield create_context(self.dummyContext)
        except Exception as excp:
            print "Fail fill_data/create_context: %s" % excp

        self.dummyContext['contexts'] = [ self.dummyContext['context_gus'] ]
        self.dummySubmission['context_gus'] = self.dummyContext['context_gus']
        self.dummySubmission['receivers'] = [ self.dummyReceiver['receiver_gus'] ]

        try:
            self.dummySubmission = yield create_submission(self.dummySubmission, finalize=True)
        except Exception as excp:
            print "Fail fill_data/create_submission: %s" % excp

        try:
            self.dummyWBTip = yield create_whistleblower_tip(self.dummySubmission)
        except Exception as excp:
            print "Fail fill_data/create_whistleblower: %s" % excp


    def setUp_dummy(self):
        self.dummyReceiver = {
            'receiver_gus': unicode(uuid.uuid4()),
            'password': DEFAULT_PASSWORD,
            'name': u'john smith',
            'description': u'the first receiver',
            'notification_fields': {'mail_address': u'maker@ggay.it'},
            'can_delete_submission': True,
            'receiver_level': 1,
            'contexts' : [],
        }
        self.dummyContext = {
            'context_gus': unicode(uuid.uuid4()),
            'name': u'created by shooter',
            'description': u'This is the update',
            'fields': [{u'hint': u'autovelox',
                        u'label': u'city',
                        u'name': u'city',
                        u'presentation_order': 1,
                        u'required': True,
                        u'type': u'text',
                        u'value': u"Yadda I'm default with apostrophe"},
                       {u'hint': u'name of the sun',
                        u'label': u'Sun',
                        u'name': u'Sun',
                        u'presentation_order': 2,
                        u'required': True,
                        u'type': u'checkbox',
                        u'value': u"I'm the sun, I've not name"},
                       {u'hint': u'put the number ',
                        u'label': u'penality details',
                        u'name': u'dict2',
                        u'presentation_order': 3,
                        u'required': True,
                        u'type': u'text',
                        u'value': u'666 the default value'},
                       {u'hint': u'details:',
                        u'label': u'how do you know that ?',
                        u'name': u'dict3',
                        u'presentation_order': 4,
                        u'required': False,
                        u'type': u'textarea',
                        u'value': u'buh ?'}],
            'selectable_receiver': False,
            'tip_max_access': 10,
            # _timetolive are expressed in seconds!
            'tip_timetolive': 200,
            'submission_timetolive': 100,
            'file_max_download' :1,
            'escalation_threshold': 1,
            'receivers' : []
        }
        self.dummySubmission = {
            'context_gus': '',
            'wb_fields': {"city":"Milan","Sun":"warm","dict2":"happy","dict3":"blah"},
            'finalize': False,
            'receivers': [],
        }
        self.dummyNode = {
             'name':  u"Please, set me: name/title",
             'description':  u"Please, set me: description",
             'hidden_service':  u"Please, set me: hidden service",
             'public_site':  u"Please, set me: public site",
             'email':  u"email@dumnmy.net",
             'stats_update_time':  2, # hours,
             'languages':  [{ "code" : "it" , "name": "Italiano"},
                            { "code" : "en" , "name" : "English" }],
             'password' : '',
             'old_password' : '',
             'salt': 'xxxxxhefdiufiwnfewifweibeifwiebfibweiufwixx',
             'salt_receipt': 'mfeiwofmeiwofmnoiwefniowefowiemfoiwefow',
        }
        self.dummyNotification = {
            'server': u'mail.foobar.xxx',
            'port': 12345,
            'username': u'staceppa',
            'password': u'antani',
            'security': u'SSL',
            'tip_template': u'tip message: %sNodeName%',
            'comment_template': u'comment message: %sNodeName%',
            'file_template': u'file message: %sNodeName%',
            'activation_template': u'activation message: %sNodeName%',
        }

class TestHandler(TestGL):
    """
    :attr _handler: handler class to be tested
    """
    _handler = None

    @inlineCallbacks
    def setUp(self):
        """
        override default handlers' get_store with a mock store used for testing/
        """
        yield TestGL.setUp(self)
        self.responses = []

        @classmethod
        def mock_write(cls, response=None):
            # !!!
            # Here we are making the assumption that every time write() get's
            # called it contains *all* of the response message.
            if response:
                self.responses.append(response)

        self._handler.write = mock_write
        # we make the assumption that we will always use call finish on write.
        self._handler.finish = mock_write

        # we need to reset settings.session to keep each test independent
        GLSetting.sessions = dict()


    def request(self, jbody=None, role=None, user_id=None, headers=None, body='',
            remote_ip='0.0.0.0', method='MOCK'):

        """
        Function userful for performing mock requests.

        Args:

            jbody:
                The body of the request as a dict (it will be automatically
                converted to string)

            body:
                The body of the request as a string

            role:
                If we should perform authentication role can be either "admin",
                "receiver" or "wb"

            user_id:
                If when performing authentication the session should be bound
                to a certain user_id.

            method:
                HTTP method, e.g. "GET" or "POST"

            uri:
                URL to fetch

            role:
                the role

            headers:
                (dict or :class:`cyclone.httputil.HTTPHeaders` instance) HTTP
                headers to pass on the request

            remote_ip:
                If a particular remote_ip should be set.

        """
        if jbody and not body:
            body = json.dumps(jbody)
        elif body and jbody:
            raise ValueError('jbody and body in conflict')

        application = Application([])

        tr = proto_helpers.StringTransport()
        connection = httpserver.HTTPConnection()
        connection.factory = application
        connection.makeConnection(tr)

        request = httpserver.HTTPRequest(uri='mock',
                                         method=method,
                                         headers=headers,
                                         body=body,
                                         remote_ip=remote_ip,
                                         connection=connection)

        handler = self._handler(application, request)
        if role:
            session_id = '4tehlulz'
            new_session = OD(
                   timestamp=time.time(),
                   id=session_id,
                   role=role,
                   user_id=user_id
            )
            GLSetting.sessions[session_id] = new_session
            handler.request.headers['X-Session'] = session_id
        return handler