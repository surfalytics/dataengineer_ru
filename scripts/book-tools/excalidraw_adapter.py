#!/usr/bin/env python3
"""Serve the diagram builders' canvas API over a local mcp_excalidraw renderer."""

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import ProxyHandler, Request, build_opener


class CanvasAdapter(HTTPServer):
    def __init__(self, port, renderer_port):
        super().__init__(("127.0.0.1", port), CanvasHandler)
        self.renderer_url = f"http://127.0.0.1:{renderer_port}"
        self.opener = build_opener(ProxyHandler({}))
        self.current = None

    def render_request(self, method, path, body=None):
        request = Request(
            self.renderer_url + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method=method,
        )
        with self.opener.open(request, timeout=55) as response:
            return json.load(response)

    def scene_names(self):
        response = self.render_request("GET", "/api/snapshots")
        return [snapshot["name"] for snapshot in response["snapshots"]]

    def select_scene(self, name, *, create):
        if not isinstance(name, str) or not name.strip():
            return HTTPStatus.BAD_REQUEST, {"error": "Scene name is required"}

        if create:
            if name in self.scene_names():
                return HTTPStatus.CONFLICT, {"error": f"Scene already exists: {name}"}
            self.render_request("DELETE", "/api/elements/clear")
            self.current = None
            self.render_request("POST", "/api/snapshots", {"name": name})
        else:
            response = self.render_request("GET", "/api/snapshots/" + quote(name, safe=""))
            self.render_request("POST", "/api/elements/sync", {
                "elements": response["snapshot"]["elements"],
            })

        self.current = name
        return HTTPStatus.OK, {"success": True, "current": name}

    def dispatch(self, method, path, body):
        match method, path:
            case "GET", "/api/scenes":
                return HTTPStatus.OK, {"current": self.current, "scenes": self.scene_names()}
            case "POST", "/api/scenes" | "/api/scenes/open":
                return self.select_scene(body.get("name"), create=path == "/api/scenes")
            case "POST", "/api/scenes/save":
                if self.current is None:
                    return HTTPStatus.CONFLICT, {"error": "Select a scene before saving"}
                return HTTPStatus.OK, self.render_request("POST", "/api/snapshots", {
                    "name": self.current,
                })
            case "POST", "/api/export/image":
                result = self.render_request("POST", path, {"renderer": "node", **body})
                if body.get("format") == "png":
                    result["data"] = result["data"].removeprefix("data:image/png;base64,")
                return HTTPStatus.OK, result
            case ("GET", "/health" | "/api/elements") | ("POST", "/api/elements/batch"):
                return HTTPStatus.OK, self.render_request(method, path, body)
            case "DELETE", element_path if element_path.startswith("/api/elements/"):
                return HTTPStatus.OK, self.render_request(method, element_path)
            case _:
                return HTTPStatus.NOT_FOUND, {"error": "Unsupported canvas route"}


class CanvasHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        try:
            body = None
            if self.command == "POST":
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 <= length <= 10 * 1024 * 1024:
                    self.reply(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Canvas request is too large"})
                    return
                body = json.loads(self.rfile.read(length)) if length else {}
                if not isinstance(body, dict):
                    raise ValueError("Expected a JSON object")
        except ValueError:
            self.reply(HTTPStatus.BAD_REQUEST, {"error": "Expected a JSON object"})
            return

        try:
            status, response = self.server.dispatch(self.command, urlsplit(self.path).path, body)
        except HTTPError as error:
            status = error.code
            with error:
                try:
                    response = json.load(error)
                except ValueError:
                    response = {"error": error.reason}
        except (URLError, ValueError, TimeoutError) as error:
            status, response = HTTPStatus.BAD_GATEWAY, {"error": f"Canvas renderer: {error}"}
        self.reply(status, response)

    def reply(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_DELETE = handle_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=3456, help="adapter port (default: 3456)")
    parser.add_argument("--renderer-port", type=int, default=3457, help="mcp_excalidraw port (default: 3457)")
    args = parser.parse_args()
    if args.port == args.renderer_port:
        parser.error("adapter and renderer must use different ports")

    with CanvasAdapter(args.port, args.renderer_port) as server:
        print(f"Canvas adapter on http://127.0.0.1:{args.port} -> {server.renderer_url}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
