import csv
from io import StringIO
import random
import requests
import matplotlib.pyplot as plt
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///solar_data.db'
db = SQLAlchemy(app)


class SolarData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    energy_produced = db.Column(db.Float, nullable=False)
    efficiency = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    maintenance_status = db.Column(db.String(50), nullable=False)
    needs_alert = db.Column(db.Boolean, default=False, nullable=False)


def generate_health_metrics_image():
    total_installations = SolarData.query.count()
    maintenance_required = SolarData.query.filter_by(maintenance_status="Needs Maintenance").count()
    low_efficiency = SolarData.query.filter(SolarData.efficiency < 75).count()
    good_condition = total_installations - (maintenance_required + low_efficiency)

    labels = ['Good Condition', 'Needs Maintenance', 'Low Efficiency']
    sizes = [good_condition, maintenance_required, low_efficiency]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig.savefig('static/health_metrics.png')

    # close the figure
    plt.close(fig)


def fetch_and_store_data():
    with app.app_context():  # Push an application context
        response = requests.get('http://127.0.0.1:5000/solar_data')
        data = response.json()

        for installation in data:
            solar_data = SolarData(
                latitude=installation['latitude'],
                longitude=installation['longitude'],
                energy_produced=installation['energy_produced'],
                efficiency=installation['efficiency'],
                temperature=installation['temperature'],
                maintenance_status=installation['maintenance_status']
            )
            db.session.add(solar_data)
        db.session.commit()

        # Generate health metrics image after storing data
        generate_health_metrics_image()


scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_data, 'interval', seconds=10)
scheduler.start()


@app.route('/solar_data', methods=['GET'])
def get_data():
    data = [{
        "latitude": random.uniform(-90, 90),
        "longitude": random.uniform(-180, 180),
        "energy_produced": random.uniform(1000, 5000),  # kWh
        "efficiency": random.uniform(75, 100),  # in percentage
        "temperature": random.uniform(15, 40),  # degree Celsius
        "maintenance_status": random.choice(["Good", "Needs Maintenance"])
    } for _ in range(5)]  # Generate data for 5 installations for demonstration purposes
    return jsonify(data)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Fetch data
    data = SolarData.query.all()

    # Overview metrics
    total_installations = len(data)
    maintenance_required = sum(1 for installation in data if installation.maintenance_status == "Needs Maintenance")
    average_efficiency = sum(installation.efficiency for installation in data) / total_installations
    total_energy_today = sum(installation.energy_produced for installation in data)

    # Top 5 and Bottom 5 by efficiency
    top_5 = SolarData.query.order_by(SolarData.efficiency.desc()).limit(5).all()
    bottom_5 = SolarData.query.order_by(SolarData.efficiency).limit(5).all()

    return render_template('dashboard.html', data=data,
                           total_installations=total_installations,
                           maintenance_required=maintenance_required,
                           average_efficiency=average_efficiency,
                           total_energy_today=total_energy_today,
                           top_5=top_5, bottom_5=bottom_5)


@app.route('/report/daily', methods=['GET'])
def daily_report():
    data = SolarData.query.all()  # You can modify this to filter by date for daily data
    si = StringIO()
    cw = csv.writer(si)

    # Write header
    cw.writerow(['Latitude', 'Longitude', 'Energy Produced', 'Efficiency', 'Temperature', 'Maintenance Status'])

    # Write data
    for installation in data:
        cw.writerow(
            [installation.latitude, installation.longitude, installation.energy_produced, installation.efficiency,
             installation.temperature, installation.maintenance_status])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=daily_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/graphical_report', methods=['GET'])
def graphical_report():
    # You can extend this if you want more graphs or different representations.
    return render_template('graph_report.html')


if __name__ == '__main__':
    app.run(debug=True)
