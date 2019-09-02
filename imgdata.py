from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import timedelta, datetime
import imgprc
import sys
import os
import io
db = SQLAlchemy()


class photo(db.Model):
    # pylint: disable=E1101
    __tableneme__ = "photos"
    file_name = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.TIMESTAMP(
        timezone=False), server_default=func.now())
    image = db.Column(db.LargeBinary, nullable=False)
    image_t = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return "<photo filename:{},created time:{}>".format(self.file_name, self.created_date)


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def addPhoto(image):
    # pylint: disable=E1101
    memspace = io.BytesIO()
    memspaceOrg = io.BytesIO()
    image.save(memspaceOrg)
    p = photo()
    p.image = memspaceOrg.getvalue()
    t = imgprc.createThumbnail(image)
    t.save(memspace,format="JPEG")
    p.image_t = memspace.getvalue()
    db.session.add(p)
    db.session.commit()
    memspace.close()
    memspaceOrg.close()


def getFileList(clExist):
    # pylint: disable=E1101
    dbExist = db.session.query(func.count(photo.file_name)).scalar()
    list = photo.query.order_by(
        photo.created_date.desc()).limit(dbExist - clExist).all()
    return list


def getFile(filename):
    cachePath = "/tmp/iu/"
    img = photo.query.filter(photo.file_name == filename).first()
    if img is not None:
        with open(os.path.join(cachePath, str(img.file_name)), "wb") as out:
            out.write(img.image)
        with open(os.path.join(cachePath, str(img.file_name)+"_t"), "wb") as out:
            out.write(img.image_t)
    return img


def deleteFile(num):
    # pylint: disable=E1101
    import index
    with index.app.app_context():
        two_days = timedelta(days=2)
        if num == "all":
            p = db.session.query(photo).delete()
        else:
            p = db.session.query(photo).filter(
                photo.created_date < datetime.now() - two_days).delete()
        print(p)
        db.session.commit()
        return p


if __name__ == "__main__":
    if len(sys.argv) == 2:
        p = deleteFile(sys.argv[1])
        print("deleted {} photo(s)").format(p)
    else:
        pass
