from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

application = Flask(__name__)

# # Configuration for RDS MySQL database
db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')

#application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:data_base@database-2.cl28cccywk7a.ap-south-1.rds.amazonaws.com:3306/mydb'
uri = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:3306/{db_name}'
application.config['SQLALCHEMY_DATABASE_URI'] = str(uri)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
first_request = True
db = SQLAlchemy(application)

# Define a simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
@application.before_request
def before_first_request():
    global first_request
    if first_request:
        db.create_all()        
        first_request = False

# CRUD routes
@application.route('/')
def hello():
    return "Hello World!"
@application.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@application.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])

@application.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@application.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.name = data['name']
    user.email = data['email']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@application.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80)