
import mimetypes
import os
import uuid
from urllib.parse import quote

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import select
from werkzeug.utils import secure_filename

from config import Config
from extensions import db
from models import StoredFile
from storage import create_r2_client


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CSRFProtect(app)

    r2 = create_r2_client(app)
    bucket = app.config["R2_BUCKET_NAME"]

    def public_url(object_key):
        base = app.config["R2_PUBLIC_BASE_URL"]
        encoded_key = quote(object_key, safe="/")
        return f"{base}/{encoded_key}"

    def normalize_folder(value):
        parts = [
            part.strip()
            for part in value.replace("\\", "/").split("/")
            if part.strip() and part.strip() not in (".", "..")
        ]
        return "/".join(parts)[:512]

    def get_file(file_id):
        stored_file = db.session.get(StoredFile, file_id)
        if stored_file is None:
            abort(404)
        return stored_file

    @app.get("/")
    def index():
        folder = normalize_folder(request.args.get("folder", ""))
        search = request.args.get("q", "").strip()

        query = select(StoredFile)

        if folder:
            query = query.where(StoredFile.folder == folder)

        if search:
            query = query.where(
                StoredFile.filename.contains(search)
            )

        files = db.session.execute(
            query.order_by(StoredFile.created_at.desc())
        ).scalars().all()

        folder_query = select(StoredFile.folder).distinct()
        folders = sorted(
            name
            for name in db.session.execute(folder_query).scalars()
            if name
        )

        return render_template(
            "index.html",
            files=files,
            folders=folders,
            current_folder=folder,
            search=search,
            public_url=public_url,
        )

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if request.method == "POST":
            uploaded = request.files.get("file")
            folder = normalize_folder(request.form.get("folder", ""))

            if not uploaded or not uploaded.filename:
                flash("Choose a file to upload.", "error")
                return redirect(url_for("upload"))

            filename = secure_filename(uploaded.filename)

            if not filename:
                flash("Invalid filename.", "error")
                return redirect(url_for("upload"))

            payload = uploaded.stream.read(
                app.config["MAX_CONTENT_LENGTH"] + 1
            )

            if len(payload) > app.config["MAX_CONTENT_LENGTH"]:
                flash("File exceeds the upload limit.", "error")
                return redirect(url_for("upload"))

            content_type = (
                uploaded.mimetype
                or mimetypes.guess_type(filename)[0]
                or "application/octet-stream"
            )

            object_key = (
                f"{folder}/{uuid.uuid4().hex}_{filename}"
                if folder
                else f"{uuid.uuid4().hex}_{filename}"
            )

            try:
                r2.put_object(
                    Bucket=bucket,
                    Key=object_key,
                    Body=payload,
                    ContentType=content_type,
                )

                stored_file = StoredFile(
                    filename=filename,
                    object_key=object_key,
                    folder=folder,
                    content_type=content_type,
                    size_bytes=len(payload),
                )

                db.session.add(stored_file)
                db.session.commit()

            except (BotoCoreError, ClientError):
                db.session.rollback()
                app.logger.exception("R2 upload failed")
                flash("Storage upload failed.", "error")
                return redirect(url_for("upload"))

            except Exception:
                db.session.rollback()

                # Avoid leaving an orphaned object after a DB failure.
                try:
                    r2.delete_object(
                        Bucket=bucket,
                        Key=object_key,
                    )
                except Exception:
                    app.logger.exception(
                        "Could not clean up uploaded R2 object"
                    )

                app.logger.exception("Metadata save failed")
                flash("Could not save file metadata.", "error")
                return redirect(url_for("upload"))

            flash("File uploaded successfully.", "success")
            return redirect(url_for("index", folder=folder))

        return render_template("upload.html")

    @app.get("/download/<int:file_id>")
    def download(file_id):
        stored_file = get_file(file_id)

        try:
            response = r2.get_object(
                Bucket=bucket,
                Key=stored_file.object_key,
            )
            body = response["Body"]

            try:
                return send_file(
                    body,
                    mimetype=stored_file.content_type,
                    as_attachment=True,
                    download_name=stored_file.filename,
                )
            except Exception:
                body.close()
                raise

        except (BotoCoreError, ClientError):
            app.logger.exception("File download failed")
            abort(502)

    @app.get("/preview/<int:file_id>")
    def preview(file_id):
        stored_file = get_file(file_id)

        # Only render known inline media types.
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "application/pdf",
            "video/mp4",
            "audio/mpeg",
        }

        if stored_file.content_type not in allowed_types:
            abort(415)

        response = r2.get_object(
            Bucket=bucket,
            Key=stored_file.object_key,
        )

        return send_file(
            response["Body"],
            mimetype=stored_file.content_type,
            as_attachment=False,
            download_name=stored_file.filename,
        )

    @app.post("/delete/<int:file_id>")
    def delete_file(file_id):
        stored_file = get_file(file_id)

        try:
            r2.delete_object(
                Bucket=bucket,
                Key=stored_file.object_key,
            )

            db.session.delete(stored_file)
            db.session.commit()

        except Exception:
            db.session.rollback()
            app.logger.exception("File deletion failed")
            flash("Could not delete file.", "error")
            return redirect(url_for("index"))

        flash("File deleted.", "success")
        return redirect(
            url_for("index", folder=stored_file.folder)
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="127.0.0.1", port=8000, debug=False)
