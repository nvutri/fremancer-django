from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient


class UsersTestCase(TestCase):
    """Testing the handling of users."""

    def setUp(self):
        """Setup default client and user."""
        c = Client()
        c.post('/api/users/', {
            'username': 'test1@yahoo.com',
            'email': 'test1@yahoo.com',
            'password': '12345678',
            'first_name': 'firstN',
            'last_name': 'lastN',
            'membership': 'freelancer'
        })

    def test_create_new_user(self):
        """Test creating new user."""
        c = Client()
        response = c.post('/api/users/', {
            'email': 'test3@yahoo.com',
            'password': '12345678',
            'first_name': 'firstN',
            'last_name': 'lastN',
            'membership': 'freelancer'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json().get('error'))
        self.assertTrue(User.objects.filter(username='test1@yahoo.com').exists())

    def test_create_duplicated_user(self):
        """Test creating duplicating user."""
        c = Client()
        c_request = {
            'email': 'test2@yahoo.com',
            'password': '12345678',
            'first_name': 'firstN',
            'last_name': 'lastN',
            'membership': 'freelancer'
        }
        response = c.post('/api/users/', c_request)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json().get('error'))
        self.assertTrue(User.objects.filter(username='test2@yahoo.com').exists())
        response = c.post('/api/users/', c_request)
        self.assertIsNotNone(response.json().get('error'))
        self.assertTrue('email' in response.json().get('error'))

    def test_password(self):
        """Test issues related to passwords."""
        c = Client()
        c_request = {
            'email': 'test3@yahoo.com',
            'password': '',
            'first_name': 'firstN',
            'last_name': 'lastN',
            'membership': 'freelancer'
        }
        response = c.post('/api/users/', c_request)
        self.assertIsNotNone(response.json().get('error'))
        self.assertTrue('password' in response.json().get('error'))
        c_request['password'] = '1234'
        response = c.post('/api/users/', c_request)
        self.assertIsNotNone(response.json().get('error'))
        self.assertTrue('password' in response.json().get('error'))
        c_request['password'] = '123456778'
        response = c.post('/api/users/', c_request)
        self.assertIsNone(response.json().get('error'))

    def test_login_user(self):
        """Test user login."""
        c = Client()
        response = c.post('/api/users/authenticate/', {
            'username': 'test1@yahoo.com',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        response = c.post('/api/users/authenticate/', {
            'username': 'test1@yahoo.com',
            'password': '123'
        })
        # Failed request.
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json())

    def test_user_is_authenticated(self):
        c = Client()
        response = c.post('/api/users/authenticate/', {
            'username': 'test1@yahoo.com',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        response = c.post('/api/users/is_authenticated/')
        self.assertTrue(response.json().get('success'))
        response = c.post('/api/users/logout/')
        self.assertEqual(response.status_code, 200)
        response = c.post('/api/users/is_authenticated/')
        self.assertFalse(response.json().get('success'))

    def test_logout_user(self):
        """Test logout user."""
        c = Client()
        response = c.post('/api/users/authenticate/', {
            'username': 'test1@yahoo.com',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        response = c.post('/api/users/logout/')
        self.assertEqual(response.status_code, 200)

    def test_create_and_filter_profile(self):
        """Test create a new user and filter membership."""
        c = Client()
        user_profile = {
            'email': 'test1@yahoo.com',
            'password': '12345678',
            'first_name': 'firstN',
            'last_name': 'lastN',
            'membership': 'freelancer'
        }
        c.post('/api/users/', user_profile)
        user_profile['email'] = 'test2@yahoo.com'
        c.post('/api/users/', user_profile)
        user_profile['email'] = 'test3@yahoo.com'
        user_profile['membership'] = 'hirer'
        c.post('/api/users/', user_profile)
        # Authenticate to do a GET request.
        c = APIClient()
        c.force_authenticate(user=User.objects.get(username='test1@yahoo.com'))
        response = c.get('/api/profiles/')
        result = response.json()
        self.assertEqual(result.get('count'), 3)
        response = c.get('/api/profiles/?membership=freelancer')
        result = response.json()
        self.assertEqual(result.get('count'), 2)
