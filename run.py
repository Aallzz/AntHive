#!/usr/bin/env python

import json
import random
import math

try:  # For python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:  # For python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

ACTIONS = ["move", "eat", "load", "unload"]
DIRECTIONS = ["up", "down", "right", "left"]
MOVEID = {
    (-1, 0): 0,
    (1, 0): 1,
    (0, 1): 2,
    (0, -1): 3    
}

temp_map = {}

def parseJSON(json):
    return json["map"]["height"], json["map"]["width"], reversed(json["cells"]), json["id"], json["ants"]


def getDist(x, y, xx, yy):
    return abs(x - xx) + abs(y - yy)

def findNearestItem(mapa, x, y, item):
    res = math.inf
    px, py = 0, 0
    for yy, line in enumerate(mapa):
        for xx, e in enumerate(line):
            if item in e and len(e) == 1:
                if ((xx, yy) in temp_map):
                    continue
                curD = getDist(x, y, xx, yy)
                if (curD < res):
                    px, py, res = xx, yy, curD
    temp_map[(px, py)] = 1
    return px, py, res
   
def getDirTo(mapa, x, y, xx, yy):
    d = math.inf
    rx, ry = 1, 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if abs(dx) + abs(dy) != 1:
                continue
            if ("ant" in mapa[y][x]):
                continue
            curD = getDist(x + dx, y + dy, xx, yy)
            if (curD < d):
                rx, ry, d = dx, dy, curD
    return rx, ry


def naiveChooseAction(mapa, ant, x, y):
    if ("food" in mapa[y][x]):
        return "load"
    elif ("hive" in mapa[y][x]):
        return "unload"
    elif (ant["health"] == 1):
        return "eat"
    else:
        return "move"

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        payload = self.rfile.read(int(self.headers['Content-Length']))

        # Hive object from request payload
        hive = json.loads(payload)
        height, width, mapa, hiveId, ants = parseJSON(hive)
        orders = {}
        for ant in ants:
            x, y, d = 0,0,0
            if (ant["payload"] == 0):
                x, y, d = findNearestItem(mapa, ant["x"], ant["y"], "food")
            else:
                x, y, d = findNearestItem(mapa, ant["x"], ant["y"], "hive")
            dy, dx = getDirTo(mapa, ant["x"], ant["y"], x, y)

            orders[ant] = {
                "dir": ACTIONS[MOVEID[(dx, dy)]],
                "act": naiveChooseAction(mapa, ant, x + dx, y + dy)
            }
        temp_map.clear()

        response = json.dumps(orders)
        print(response)

        try:  # For python 3
            out = bytes(response, "utf8")
        except TypeError:  # For python 2
            out = bytes(response)

        self.wfile.write(out)

        return


def run():
    server_address = ('0.0.0.0', 7070)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
