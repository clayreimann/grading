#! /usr/bin/python3

import cherrypy
import GradingApplication

from os import path

if __name__ == '__main__':
    root = path.dirname(__file__)
    log_f = path.join(root, "logs", "access.txt")
    err_f = path.join(root, "logs", "error.txt")
    cherrypy.config.update({
      "log.screen": False,
      "log.access_file": log_f,
      "log.error_file": err_f,
      "server.socket_host": "0.0.0.0",
      "server.socket_port": 8085
    })

    vhost = cherrypy._cpwsgi.VirtualHost(GradingApplication.grade_app)
    cherrypy.tree.graft(vhost)

    # cherrypy.tree.mount(grade_app)

    cherrypy.engine.start()
    cherrypy.engine.block()
