# flask_file
Flask File Manager

A simple, modular file manager built with Flask, allowing you to upload, download, rename, delete, and manage files and directories within a web interface. It supports drag-and-drop uploads, displays file properties, and provides a user-friendly interface styled with Bulma CSS.


## Features
```
    File Uploads: Drag-and-drop files or click to upload multiple files at once.
    File Listing: View files and folders in the current directory with details.
    Directory Navigation: Navigate through directories and subdirectories.
    Create Folders: Create new folders within the current directory.
    File and Folder Operations:
        Download: Download files directly from the interface.
        Rename: Rename files and folders via a modal popup.
        Delete: Delete files and folders with confirmation prompts.
        Properties: View file properties, including size and path. For images, a thumbnail preview is displayed.
    Responsive UI: Clean and responsive user interface using Bulma CSS and Font Awesome icons.
    Security: Path sanitization to prevent directory traversal attacks. Files are managed within a specified root directory.
```

## Installation

Make a project directory, then clone the repo
```
$ mkdir project-dir
$ cd project-dir
$ git clone https://github.com/jefmud/flask_file
```

### Create a Virtual Environment (Optional)

```
$ python3 -m venv venv
$ source venv/bin/activate
```

### Install Dependencies

```
$ pip install Flask
```

Ensure you have Flask installed. The module also uses werkzeug and Jinja2 which comes with Flask.

## Usage

Integrate into Your Flask App

1. Copy the flask_file Module

2. Copy the flask_file directory into your project.

3. Initialize in Your Flask Application

    
```python
from flask import Flask
from flask_file import FlaskFile

app = Flask(__name__)
file_manager = FlaskFile(app, url_base='/filemanager', file_root='/static/uploads')

if __name__ == '__main__':
    app.run(debug=True)
```

    Parameters:
        app: Your Flask application instance.
        url_base: The base URL where the file manager will be accessible (default is /filemanager).
        file_root: The root directory for file operations (default is /static/uploads).

## Run the Application

```
$ python main.py
```

### Access the File Manager

Open your web browser and navigate to http://localhost:5000/filemanager/.

## Directory Structure

```
flask_file/
├── __init__.py
├── flask_file.py
└── templates/
    └── flask_file/
        ├── base.html
        └── index.html
```

``__init__.py``: Makes the flask_file directory a Python package and allows for easy importing.

``flask_file.py``: Contains the FlaskFile class that sets up the file manager.

Templates: HTML templates for rendering the file manager interface.

## Security Considerations

Authentication: The module does not include user authentication. Do not deploy in a production environment without implementing proper authentication and authorization mechanisms.
    
You can use your own authentication and integrate it to the FlaskFile object and assign the `is_authenticated` to a function that returns True if authenticated, or False if not.

File Sanitization: Uses `secure_filename` from werkzeug.utils to sanitize file and folder names.

Path Security: Ensures that all file operations are confined within the specified root directory to prevent directory traversal attacks.

Serving Files: Files are served securely using Flask's `send_from_directory` function.

## Customization

Styling: The interface uses Bulma CSS and Font Awesome icons. You can customize the styles by modifying the templates or overriding the CSS.

Templates: The HTML templates are located in templates/flask_file/. Feel free to modify them to suit your needs.

URL Base and File Root: Adjust the url_base and file_root parameters when initializing FlaskFile to change where the file manager is accessible and where files are stored.

## Dependencies

Flask: Web framework used for the application.

Werkzeug: Utility library used for secure filename handling (included with Flask).

Bulma CSS: For styling the user interface (included via CDN).

Font Awesome: For icons in the user interface (included via CDN).

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the Repository

2. Click the "Fork" button at the top-right corner of this page to create a copy of the repository under your GitHub account.

3. Clone Your Fork


```
$ git clone https://github.com/jefmud/flask_file
$ cd flask-file-manager
```

### Create a Feature Branch

```
$ git checkout -b feature/your-feature-name
```

### Make Changes

Implement your feature or bug fix.

### Commit and Push

```
$ git add .
$ git commit -m "Add your commit message here"
$ git push origin feature/your-feature-name
```

### Create a Pull Request

Go to the original repository on GitHub and create a pull request from your fork.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Flask: Flask is a lightweight WSGI web application framework.

Bulma CSS: Bulma is a modern CSS framework based on Flexbox.

Font Awesome: Font Awesome provides vector icons and social logos.

## Contact

For any questions or suggestions, please open an issue on GitHub or contact me at github
