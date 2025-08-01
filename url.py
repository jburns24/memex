import socket
from enum import Enum, auto
from urllib.parse import urlparse


class Scheme(Enum):
    TCP = auto()
    FILE = auto()


class URL:
    def __init__(self, url):
        # Split out the scheme
        parsed_url = urlparse(url)
        self.scheme = parsed_url.scheme.lower()
        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "http":
            self.port = 80
            self.protocol = Scheme.TCP
        if self.scheme == "https":
            self.port = 443
            self.protocol = Scheme.TCP
        if self.scheme == "file":
            self.protocol = Scheme.FILE

        # Pull out the host
        if "/" not in url:
            url = url + "/"
        self.host = parsed_url.hostname
        self.path = parsed_url.path

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

    def request(self, headers):
        if self.protocol == Scheme.TCP:
            return self.tcp_request(headers)
        elif self.protocol == Scheme.FILE:
            return self.file_request()
        else:
            assert False, "Unsupported protocol: {}".format(self.protocol)
