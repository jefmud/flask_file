# flask_file/flask_file.py

import os
import shutil
from flask import (
    Blueprint, render_template, request, abort,
    send_from_directory, jsonify, url_for
)
from werkzeug.utils import secure_filename

class FlaskFile:
    """
    A Flask extension for file management.
    """
    def __init__(self, app, url_base='/filemanager', file_root='/static/uploads', is_authenticated=True):
        """
        Initializes a FlaskFile instance.

        Args:
            app (Flask): The Flask application instance.
            url_base (str, optional): The base URL for the file manager. Defaults to '/filemanager'.
            file_root (str, optional): The root directory for file uploads. Defaults to '/static/uploads'.
            is_authenticated (bool or callable, optional): A boolean indicating whether authentication is required, or a callable that returns a boolean. Defaults to True.

        Returns:
            None
        """
        self.app = app
        self.url_base = url_base.rstrip('/')
        self.file_root = file_root
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.bp = Blueprint(
            'flask_file', __name__,
            template_folder=template_dir
        )
        self.register_routes()

        app.register_blueprint(self.bp, url_prefix=self.url_base)
        self.ensure_directory(self.root_path)

        if type(is_authenticated) == bool and is_authenticated==True:
            # if authenticate_func was not supplied by the user, then use a default of True
            self.is_authenticated = lambda: True
        else:
            # if authenticate_func was supplied by the user, should be a function that returns True or False
            self.is_authenticated = is_authenticated

    @property
    def root_path(self):
        """
        Returns the absolute path to the root directory for file uploads.

        This property concatenates the `file_root` attribute with the `root_path`
        attribute of the Flask application instance. It ensures that the resulting
        path does not have any leading or trailing slashes.

        Returns:
            str: The absolute path to the root directory for file uploads.
        """
        return os.path.join(self.app.root_path, self.file_root.strip('/'))

    def ensure_directory(self, path):
        """
        Ensures that a directory exists at the given path.
        Args:
            path (str): The path of the directory to ensure.
        Returns:
            None
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def register_routes(self):
        """
        Registers routes for the FlaskFile blueprint.

        This method sets up the URL rules for the file manager, including routes for
        listing files, uploading files, downloading files, renaming files, deleting files,
        moving files, creating directories, and serving files.

        Args:
            None

        Returns:
            None
        """
        self.bp.add_url_rule('/', 'index', self.index)
        self.bp.add_url_rule('/list', 'list_files', self.list_files, methods=['GET'])
        self.bp.add_url_rule('/upload', 'upload', self.upload, methods=['POST'])
        self.bp.add_url_rule('/download', 'download', self.download, methods=['GET'])
        self.bp.add_url_rule('/rename', 'rename', self.rename, methods=['POST'])
        self.bp.add_url_rule('/delete', 'delete', self.delete, methods=['POST'])
        self.bp.add_url_rule('/move', 'move', self.move, methods=['POST'])
        self.bp.add_url_rule('/mkdir', 'mkdir', self.mkdir, methods=['POST'])
        self.bp.add_url_rule('/properties', 'properties', self.properties, methods=['POST'])
        self.bp.add_url_rule('/files/<path:filename>', 'serve_file', self.serve_file)


    def index(self):
        """
        Handles the index route of the FlaskFile blueprint.

        This method checks if the user is authenticated. If not, it returns a 401
        Unauthorized response. Otherwise, it renders the index.html template with
        the title "Flask File Manager".

        Args:
            None

        Returns:
            The rendered index.html template or a 401 Unauthorized response.
        """
        if not self.is_authenticated():
            return abort(401)
        return render_template('flask_file/index.html', title="Flask File Manager")

    def get_abs_path(self, path):
        """
        Returns the absolute path of a given path, ensuring it is safe and within the root directory.

        Args:
            path (str): The path to be converted to an absolute path.

        Returns:
            str: The absolute path of the given path.

        Raises:
            403: If the given path is not within the root directory.
        """
        safe_path = os.path.normpath(os.path.join(self.root_path, path.strip('/\\')))
        if not safe_path.startswith(self.root_path):
            abort(403)
        return safe_path

    def list_files(self):
        """
        Handles the list_files route of the FlaskFile blueprint.

        This method checks if the user is authenticated. If not, it returns a 401
        Unauthorized response. Otherwise, it lists the files and directories in a
        given directory path, and returns the list as a JSON response.

        Args:
            dir (str): The directory path to list files from. Defaults to an empty string.

        Returns:
            A JSON response containing a list of files and directories in the given directory.
        """
        if not self.is_authenticated():
            return abort(401)
        dir_path = request.args.get('dir', '')
        abs_dir_path = self.get_abs_path(dir_path)
        if not os.path.isdir(abs_dir_path):
            abort(404)
        items = []
        for name in os.listdir(abs_dir_path):
            path = os.path.join(abs_dir_path, name)
            items.append({
                'name': name,
                'is_dir': os.path.isdir(path),
                'size': os.path.getsize(path) if os.path.isfile(path) else None,
            })
        return jsonify(items)

    def upload(self):
        """
        Handles the upload route of the FlaskFile blueprint.

        This method checks if the user is authenticated. If not, it returns a 401
        Unauthorized response. Otherwise, it retrieves the directory path from the
        request form data, ensures the directory exists, and then saves the uploaded
        files to the specified directory.

        Args:
            None

        Returns:
            A JSON response containing a success flag.
        """
        if not self.is_authenticated():
            return abort(401)
        dir_path = request.form.get('dir', '')
        abs_dir_path = self.get_abs_path(dir_path)
        self.ensure_directory(abs_dir_path)
        files = request.files.getlist('files[]')
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(abs_dir_path, filename))
        return jsonify({'success': True})

    def download(self):
        """
        Handles the download route of the FlaskFile blueprint.

        This method checks if the user is authenticated. If not, it returns a 401
        Unauthorized response. Otherwise, it retrieves the file path from the
        request arguments, ensures the file exists, and then returns the file as
        an attachment.

        Args:
            None

        Returns:
            A file attachment response.
        """
        if not self.is_authenticated():
            return abort(401)
        file_path = request.args.get('file', '')
        abs_file_path = self.get_abs_path(file_path)
        if not os.path.isfile(abs_file_path):
            abort(404)
        directory = os.path.dirname(abs_file_path)
        filename = os.path.basename(abs_file_path)
        return send_from_directory(directory, filename, as_attachment=True)

    def rename(self):
        """
        Handles the download route of the FlaskFile blueprint.

        This method checks if the user is authenticated. If not, it returns a 401
        Unauthorized response. Otherwise, it retrieves the file path from the
        request arguments, ensures the file exists, and then returns the file as
        an attachment.

        Args:
            None

        Returns:
            A file attachment response.
        """
        if not self.is_authenticated():
            return abort(401)
        old_path = request.form.get('old_path', '')
        new_name = request.form.get('new_name', '')
        abs_old_path = self.get_abs_path(old_path)
        new_name = secure_filename(new_name)
        abs_new_path = os.path.join(os.path.dirname(abs_old_path), new_name)
        if not os.path.exists(abs_old_path):
            abort(404)
        os.rename(abs_old_path, abs_new_path)
        return jsonify({'success': True})

    def delete(self):
        """
        Deletes a file or directory from the server.

        Args:
            None

        Returns:
            A JSON response indicating whether the deletion was successful.
        """
        if not self.is_authenticated():
            return abort(401)
        path = request.form.get('path', '')
        abs_path = self.get_abs_path(path)
        if not os.path.exists(abs_path):
            abort(404)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
        return jsonify({'success': True})

    def move(self):
        """
        Moves a file or directory to a specified destination.

        Args:
            src_path (str): The path of the file or directory to be moved.
            dest_dir (str): The destination directory where the file or directory will be moved.

        Returns:
            A JSON response indicating whether the move operation was successful.
        """
        if not self.is_authenticated():
            return abort(401)
        src_path = request.form.get('src_path', '')
        dest_dir = request.form.get('dest_dir', '')
        abs_src_path = self.get_abs_path(src_path)
        abs_dest_dir = self.get_abs_path(dest_dir)
        self.ensure_directory(abs_dest_dir)
        if not os.path.exists(abs_src_path):
            abort(404)
        shutil.move(abs_src_path, abs_dest_dir)
        return jsonify({'success': True})

    def mkdir(self):
        """
        Creates a new directory in the file system.

        Args:
            dir_path (str): The path of the parent directory where the new directory will be created.
            dir_name (str): The name of the new directory to be created.

        Returns:
            A JSON response indicating whether the directory creation was successful.
        """
        if not self.is_authenticated():
            return abort(401)
        dir_path = request.form.get('dir_path', '')
        dir_name = request.form.get('dir_name', '')
        dir_name = secure_filename(dir_name)
        if not dir_name or '/' in dir_name or '\\' in dir_name:
            return jsonify({'success': False, 'message': 'Invalid directory name'}), 400
        abs_dir_path = self.get_abs_path(os.path.join(dir_path, dir_name))
        if os.path.exists(abs_dir_path):
            return jsonify({'success': False, 'message': 'Directory already exists'}), 400
        try:
            os.makedirs(abs_dir_path)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    def properties(self):
        """
        Retrieves the properties of a file or directory.

        Args:
            path (str): The path of the file or directory.

        Returns:
            A JSON response containing the properties of the file or directory, including its name, path, size, and type.
        """
        path = request.form.get('path', '')
        abs_path = self.get_abs_path(path)
        if not os.path.exists(abs_path):
            return jsonify({'success': False, 'message': 'File not found'}), 404
        is_dir = os.path.isdir(abs_path)
        size = self.get_dir_size(abs_path) if is_dir else os.path.getsize(abs_path)
        data = {
            'success': True,
            'name': os.path.basename(abs_path),
            'path': abs_path,
            'size': size,
            'is_dir': is_dir,
            'is_image': False,
            'url': ''
        }
        if not is_dir and self.is_image_file(abs_path):
            data['is_image'] = True
            data['url'] = url_for('flask_file.serve_file', filename=path)
        return jsonify(data)

    def serve_file(self, filename):
        """
        Serves a file from the file system.

        Args:
            filename (str): The name of the file to be served.

        Returns:
            A response object containing the file to be served.
        """
        abs_path = self.get_abs_path(filename)
        if not os.path.exists(abs_path):
            abort(404)
        directory = os.path.dirname(abs_path)
        file_name = os.path.basename(abs_path)
        return send_from_directory(directory, file_name)

    def is_image_file(self, path):
        """
        Checks if the given file path corresponds to an image file.

        Args:
            path (str): The file path to check.

        Returns:
            bool: True if the file is an image, False otherwise.
        """
        ext = os.path.splitext(path)[1].lower()
        return ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']

    def get_dir_size(self, path):
        """
        Calculates the total size of a directory.

        Args:
            path (str): The path to the directory.

        Returns:
            int: The total size of the directory in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size
