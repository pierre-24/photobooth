from photobooth import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class Request(BaseModel):
    surname = db.Column(db.VARCHAR(length=150), nullable=False)
    name = db.Column(db.VARCHAR(length=150), nullable=False)
    email = db.Column(db.VARCHAR(length=150), nullable=False)
    pic_id = db.Column(db.Integer, nullable=False)
    note = db.Column(db.VARCHAR(length=150), nullable=False)
    add_to_newsletter = db.Column(db.Boolean, default=False, nullable=False)

    @classmethod
    def create(cls, surname: str, name: str, email: str, pic_id: int, add_to_newsletter: bool = False, note: str = ''):
        o = cls()

        o.surname = surname
        o.name = name
        o.email = email
        o.pic_id = pic_id
        o.add_to_newsletter = add_to_newsletter
        o.note = note

        return o
