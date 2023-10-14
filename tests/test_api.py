import unittest

from flask_testing import TestCase
from api import app, db, SolarData


class APITestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        # Create tables for each test
        db.create_all()

    def tearDown(self):
        # Drop all tables after each test
        db.session.remove()
        db.drop_all()

    def test_solar_data(self):
        response = self.client.get('/solar_data')
        self.assert200(response)
        data = response.get_json()
        self.assertEqual(len(data), 5)
        for installation in data:
            self.assertIn('latitude', installation)
            self.assertIn('longitude', installation)
            self.assertIn('energy_produced', installation)
            self.assertIn('efficiency', installation)
            self.assertIn('temperature', installation)
            self.assertIn('maintenance_status', installation)

    def test_dashboard(self):
        # Insert some dummy data
        installations = [
            SolarData(latitude=10, longitude=10, energy_produced=2000, efficiency=85, temperature=25,
                      maintenance_status="Good"),
            SolarData(latitude=-10, longitude=-10, energy_produced=1500, efficiency=75, temperature=30,
                      maintenance_status="Needs Maintenance"),
            # Add more if needed
        ]
        db.session.add_all(installations)
        db.session.commit()

        response = self.client.get('/dashboard')
        self.assert200(response)

    def test_daily_report(self):
        response = self.client.get('/report/daily')
        self.assert200(response)
        self.assertIn("attachment; filename=daily_report.csv", response.headers.get("Content-Disposition"))

    def test_graphical_report(self):
        response = self.client.get('/graphical_report')
        self.assert200(response)


if __name__ == '__main__':
    unittest.main()
