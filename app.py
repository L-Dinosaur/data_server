from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
DB_USERNAME = 'admin'
DB_PASSWORD = 'admin123!'
DB_HOST = 'rds-test.cb680qoi6cro.us-east-2.rds.amazonaws.com'
DB_PORT = 3306
DB_NAME = 'rds_test'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
db = SQLAlchemy(app)
api = Api(app)


class PositionModel(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Position {self.ticker}, {self.name}, {self.unit}>'

# Single record
user_args = reqparse.RequestParser()
user_args.add_argument('ticker', type=str, required=True, help='ticker is required')
user_args.add_argument('name', type=str, required=True, help='name is required')
user_args.add_argument('unit', type=str, required=False)

userFields = {
    'id': fields.Integer,
    'ticker': fields.String,
    'name': fields.String,
    'unit': fields.Integer,
}

class Positions(Resource):
    @marshal_with(userFields)
    def get(self):
        positions = PositionModel.query.all()
        return positions

    @marshal_with(userFields)
    def post(self):

        args = user_args.parse_args()
        position = PositionModel(ticker=args['ticker'], name=args['name'], unit=args.get('unit', 0))
        db.session.add(position)
        db.session.commit()
        positions = PositionModel.query.all()
        return positions, 201

class Position(Resource):
    @marshal_with(userFields)
    def get(self, position_id):
        position = PositionModel.query.filter_by(id=position_id).first()
        if not position:
            abort(404)
        return position

    @marshal_with(userFields)
    def patch(self, position_id):
        args = user_args.parse_args()
        position = PositionModel.query.filter_by(id=position_id).first()
        if not position:
            abort(404)
        position.ticker = args['ticker']
        position.name = args['name']
        position.unit = args.get('unit', position.unit)
        db.session.commit()
        return position

    @marshal_with(userFields)
    def delete(self, position_id):
        position = PositionModel.query.filter_by(id=position_id).first()
        if not position:
            abort(404)
        db.session.delete(position)
        db.session.commit()

        positions = PositionModel.query.all()
        return positions


api.add_resource(Positions, '/api/positions')
api.add_resource(Position, '/api/position/<int:position_id>')

@app.route('/')
def home():  # put application's code here
    return '<h1> Flask Project!! </h1>'


if __name__ == '__main__':
    app.run(debug=True)
