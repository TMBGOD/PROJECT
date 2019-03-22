from dbase import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User {} {}>'.format(self.id, self.username)

    @staticmethod
    def add(username, password):
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete(obj):
        db.session.delete(obj)
        db.session.commit()


class Bottle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    value = db.Column(db.Integer, unique=False, nullable=False)
    net_worth = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('bottle_list', lazy=True))

    def __repr__(self):
        return '<bottle {} {} {}>'.format(self.id, self.title, self.user_id)

    @staticmethod
    def add(title, value, type, net_worth, user):
        bottle = Bottle(title=title, value=value, type=type, net_worth=net_worth, user=user)
        db.session.add(bottle)
        db.session.commit()
        return bottle

    @staticmethod
    def delete(obj):
        db.session.delete(obj)
        db.session.commit()

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'net_worth': self.net_worth,
            'value': self.value,
            'user_id': self.user_id
        }
