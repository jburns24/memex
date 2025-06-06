import socket

class URL:
    def __init__(self, url):
        # Split out the schema
        self.schema, url = url.split("://", 1)
        assert self.schema in ["http", "https"]

        if self.schema == "http":
            self.port = 80
        if self.schema == "https":
            self.port = 443

        # Pull out the host
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )

        s.connect((self.host, self.port))

        if self.schema == "https":
            import ssl
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # Construct request and send it
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
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
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Read the content with follows the headers
        content = response.read()
        s.close()
        return content
