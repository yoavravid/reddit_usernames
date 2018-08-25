import itertools
import requests
import string
import time
import bs4

class RedditSession():
    '''
    a class used for managing a session with reddit.com
    note: it is mostly useful since it takes care of the cookies and the csrf token for you
    '''

    REDDIT_URL = 'https://www.reddit.com'
    INITIAL_COOKIES = {'rseor3': 'true'}
    INITIAL_HEADERS = {'user-agent': 'my_crazy_bot'}

    def __init__(self):
        self._cookies = self.INITIAL_COOKIES
        self._headers = self.INITIAL_HEADERS
        self._headers['cookies'] = self._cookies_as_string

        self._csrf_token = ''
        self._payload = {}



    @property
    def headers(self):
        self._headers['cookies'] = self._cookies_as_string
        return self._headers


    def init(self):
        # logic: 1st request to get the session tracker, 2nd request (to register) to get the csrf token and cookies
        # then 'rolling' requests to check_username while updating the cookies every time

        self._cookies['session-tracker'] = self._get_session_tracker()
        register_request = requests.get(self.REDDIT_URL + '/register', headers=self.headers)
        self._initialize_cookies(register_request)
        self._csrf_token = self._get_csrf_token(register_request)
        self._payload['csrf_token'] = self._csrf_token

    def is_username_free(self, username):
        self._payload['user'] = username
        response = requests.request(
            'POST',
            self.REDDIT_URL + '/check_username',
            headers=self.headers,
            data=self._payload
        )

        if response.status_code == 200:
            return True

        elif response.status_code == 400:
            return False

        else:
            raise ValueError('Got unexpected return code {}'.format(response.status_code))

    @property
    def _cookies_as_string(self):
        return '; '.join('='.join(item) for item in self._cookies.items())

    def _get_session_tracker(self):
        response = requests.get(self.REDDIT_URL, headers=self.headers)
        return response.cookies['session_tracker']

    def _initialize_cookies(self, register_request):
        ''' initializes the cookies according to the http response '''

        # note: the headers['set-cookie'] value is a string in the cookie format: 'cookie=value; cookie=value',
        #   hence there is no need to reform it into a dict, and we can use as it is
        self._headers['cookies'] += register_request.headers['set-cookie']

    def _get_csrf_token(self, register_request):
        ''' returns the csrf token '''

        bs = bs4.BeautifulSoup(
            register_request.content,
            'html.parser'
        )
        csrf_tokens = set(html_input for html_input in bs.find_all('input') if html_input['name'] == 'csrf_token')

        if len(csrf_tokens) != 1:
            raise ValueError('Found invalid amout of csrf_tokens. Found {}, expecting {}'.format(len(csrf_tokens), 1))

        return csrf_tokens.pop()['value']
