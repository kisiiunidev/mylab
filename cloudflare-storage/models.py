from datetime import datetime, timezone

from extensions import db


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class StoredFile(db.Model):
    __tablename__ = "stored_files"

    id = db.Column(db.Integer, primary_key=True)

    # Original filename shown in the dashboard
    filename = db.Column(db.String(255), nullable=False)

    # Unique object key stored in R2
    object_key = db.Column(db.String(1024), unique=True, nullable=False)

    # Virtual folder, such as documents/invoices
    folder = db.Column(
        db.String(512),
        nullable=False,
        default=""
    )

    content_type = db.Column(
        db.String(255),
        nullable=False,
        default="application/octet-stream"
    )

    size_bytes = db.Column(db.BigInteger, nullable=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "folder": self.folder,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
        }
