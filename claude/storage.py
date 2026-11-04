from flask import current_app
# For development, we'll use local file storage
# In production, you can configure for Cloudflare R2 or other cloud storage

def setup_storage(app):
    # Configure for local development
    app.config['STORAGE_TYPE'] = 'local'

    # Return a LocalStorage instance that will handle app context lazily
    return LocalStorage()

class LocalStorage:
    def __init__(self, upload_folder=None):
        # Accept upload_folder as parameter for testing
        self.upload_folder = upload_folder

    def _get_upload_folder(self):
        # Lazy evaluation to avoid app context issues
        if self.upload_folder is None:
            from flask import current_app
            with current_app.app_context():
                self.upload_folder = current_app.config['UPLOAD_FOLDER']
        return self.upload_folder

    def upload(self, file, filename):
        upload_folder = self._get_upload_folder()
        filepath = upload_folder / filename
        file.save(filepath)
        return str(filepath)

    def get_url(self, filename):
        return f"/static/uploads/{filename}"

    def delete(self, filename):
        upload_folder = self._get_upload_folder()
        filepath = upload_folder / filename
        if filepath.exists():
            filepath.unlink()