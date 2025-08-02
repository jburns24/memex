import socket
import base64
from enum import Enum, auto
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)


class Scheme(Enum):
    TCP = auto()
    FILE = auto()
    DATA = auto()


class URL:
    def __init__(self, url):
        # Split out the scheme
        parsed_url = urlparse(url)
        self.scheme = parsed_url.scheme.lower()
        assert self.scheme in ["http", "https", "file", "data"]

        if self.scheme == "http":
            self.port = 80
            self.scheme_enum = Scheme.TCP
        if self.scheme == "https":
            self.port = 443
            self.scheme_enum = Scheme.TCP
        if self.scheme == "file":
            self.scheme_enum = Scheme.FILE
        if self.scheme == "data":
            self.scheme_enum = Scheme.DATA

        self.host = parsed_url.hostname
        self.path = parsed_url.path

    def parse_data_path(self, path):
        # Split path into MIME type and data at the first comma
        mime_data = path.split(",", 1)
        logging.info("mime_type: {}".format(mime_data))
        if len(mime_data) < 2:
            mime_data.append("")  # Handle cases like "data:," or "data:text/plain,"

        mime_type, data = mime_data
        is_base64 = mime_type.endswith(";base64")

        # Remove ;base64 from MIME type if present
        if is_base64:
            mime_type = mime_type[:-7]

        # If no MIME type specified, default to text/plain
        if not mime_type:
            mime_type = "text/plain;charset=US-ASCII"

        return mime_type, is_base64, data

    def tcp_request(self, headers):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))

        if self.scheme == "https":
            import ssl

            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # Construct request and send it
        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: close\r\n"
        for header in headers:
            request += "{}\r\n".format(header)
        request += "\r\n"
        s.send(request.encode("utf8"))

        # Read in response
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        # Begin parsing response
        statusline = response.readline()
        version, status, explination = statusline.split(" ", 2)

        # Process all the headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Read the content with follows the headers
        content = response.read()
        s.close()
        return content

    def file_request(self):
        content = ""
        with open(self.path, "r") as file:
            content = file.read()
        return content

    def data_request(self, mime_type, is_base64, data):
        if mime_type.startswith("text/plain") or mime_type.startswith("text/html"):
            content = data
            if is_base64:
                content = base64.b64decode(data).decode("utf-8")
            return content
        else:
            assert False, "Unsupported mime_type"
            return data

    def request(self, headers):
        if self.scheme_enum == Scheme.TCP:
            return self.tcp_request(headers)
        elif self.scheme_enum == Scheme.FILE:
            return self.file_request()
        elif self.scheme_enum == Scheme.DATA:
            mime_type, is_base64, data = self.parse_data_path(self.path)
            content = self.data_request(mime_type, is_base64, data)
            logging.info("content from data_request: {}".format(content))
            return content
        else:
            assert False, "Unsupported protocol: {}".format(self.scheme_enum)
