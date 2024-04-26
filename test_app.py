import unittest
from app import app, flight_info, users

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_flights_route(self):
        response = self.app.get('/flights')
        self.assertEqual(response.status_code, 200)

    def test_search_route(self):
        response = self.app.get('/search')
        self.assertEqual(response.status_code, 200)

    def test_book_route(self):
        response = self.app.get('/book')
        self.assertEqual(response.status_code, 200)

    def test_admin_route(self):
        response = self.app.get('/admin')
        self.assertEqual(response.status_code, 200)

    def test_admin_panel_route(self):
        response = self.app.get('/admin/panel')
        self.assertEqual(response.status_code, 200)

    def test_admin_logout_route(self):
        response = self.app.get('/admin/logout')
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_login_route(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_logout_route(self):
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_flight_route_with_valid_id(self):
        response = self.app.get('/flight/1')
        self.assertEqual(response.status_code, 200)

    def test_discussion_route(self):
        response = self.app.get('/discussion')
        self.assertEqual(response.status_code, 200)

    def test_add_discussion_message_route(self):
        response = self.app.post('/add_discussion_message')
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_profile_route_without_session(self):
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_profile_route_with_session(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1  # Assuming user_id 1 exists
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 200)

    def test_add_to_booked_route_without_session(self):
        response = self.app.post('/add_to_booked/1')
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_add_to_booked_route_with_session(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1  # Assuming user_id 1 exists
        response = self.app.post('/add_to_booked/1')
        self.assertEqual(response.status_code, 302)  # Should redirect

if __name__ == '__main__':
    unittest.main()
