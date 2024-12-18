"""
Module with HttpHandler class, which processes the request to the web server.

HttpHandler is a class, inherited from BaseHTTPRequestHandler, and overrides
do_GET and do_POST methods to process corresponding requests.

"""

import json
import logging
import mimetypes
import os
import pathlib
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader

# налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

# Шлях до файлу
data_path = "storage/data.json"


class HttpHandler(BaseHTTPRequestHandler):
    """
    Class to handle HTTP requests and responses.

    The class is used to generate HTTP response to the client.
    It overrides the do_GET and do_POST methods of the BaseHTTPRequestHandler.
    """

    def do_GET(self):
        """Respond to a GET request.

        The response is an HTML page. The path to the page is determined by the self.path attribute.
        The method sends the HTML page as a response to the client.
        """
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("./index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("./message.html")
        elif pr_url.path == "/read.html":
            self.generate_jinja_read()
            self.send_html_file("./read.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def generate_jinja_read(self, template_path="read_jinja_tpl.html"):
        """
        Generate HTML page using Jinja2 template.
        """
        env = Environment(loader=FileSystemLoader("."))
        read_template = env.get_template(template_path)
        messages = self.read_messages(data_path)
        logging.debug(json.dumps(messages, indent=4))
        output = read_template.render(messages=messages)
        with open("read.html", "w", encoding="utf-8") as file:
            file.write(output)
        return "read.html"

    def read_messages(self, data_path):
        """
        Read messages from a JSON file and return them as a list of dictionaries.
        """
        with open(data_path, "r", encoding="utf-8") as file:
            try:
                messages = json.load(file)
            except json.JSONDecodeError:
                messages = {}
        return messages

    def do_POST(self):
        """
        Handle POST request.

        Saves the request content to "data.json" and redirects to the home page.
        """
        data = self.rfile.read(int(self.headers["Content-Length"]))
        logging.debug(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        logging.debug(data_parse)
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data_dict = {
            time_stamp: {
                key: value
                for key, value in [el.split("=") for el in data_parse.split("&")]
            }
        }
        logging.debug(data_dict)

        # Створення директорії, якщо вона не існує
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

        # Запис даних у файл
        if os.path.exists(data_path):
            with open(data_path, "r+", encoding="utf-8") as file:
                messages = self.read_messages(data_path)
                messages.update(data_dict)  # Оновлення даних
                file.seek(0)
                json.dump(messages, file, indent=4)
                file.truncate()
        else:
            with open(data_path, "w", encoding="utf-8") as file:
                json.dump(data_dict, file, indent=4)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        """
        Sends an HTML file as a response.

        Args:
            filename (str): The path to the HTML file.
            status (int, optional): The HTTP status code. Defaults to 200.

        Returns:
            None
        """
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        """
        Sends a static file as a response.

        The path to the static file is determined by the self.path attribute.

        Returns:
            None
        """
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    """
    Runs the HTTP server.

    This function sets up the server address and initializes the HTTP server
    with the specified handler class. It starts the server to listen for
    incoming connections and serves them using the handler class.

    Args:
        server_class (type, optional): The class to use for the server. Defaults
        to HTTPServer. handler_class (type, optional): The class to handle HTTP
        requests. Defaults to HttpHandler.

    Returns:
        None

    Raises:
        KeyboardInterrupt: If the server is interrupted by the user.
    """

    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
