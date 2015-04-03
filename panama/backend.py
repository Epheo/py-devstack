#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Thibaut Lapierre <root@epheo.eu>. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import docker
from panama import view, model
import json


class Image(object):

    def __init__(self, service_name):
        self.name = service_name
        self.dico = model.Dico(self.name)
        self.configfile = model.ConfigFile()

        self.dockerapi = docker.Client(base_url=self.configfile.docker_url,
                                       version=self.configfile.docker_version,
                                       timeout=10)

    def build(self, nocache):
        if self.dico.tag is not None:
            for line in self.dockerapi.build(path=self.dico.path,
                                             tag=self.dico.tag,
                                             nocache=nocache):
                jsonstream =  json.loads(line.decode())
                stream = jsonstream.get('stream')
                error = jsonstream.get('error')
                if not error == None:
                    print(error)
                if not stream == None:
                    print(stream)


        else:
            print("Unrecognized service name")

    def create(self):
        self.dockerapi.create_container(image=self.dico.tag,
                                        name=self.name,
                                        detach=False,
                                        ports=self.dico.ports,
                                        environment=self.configfile.template_vars,
                                        volumes=self.dico.volumes,
                                        hostname=self.dico.name)


class Container(object):

    def __init__(self, service_name):
        self.name = service_name
        self.dico = model.Dico(self.name)
        self.tag = self.dico.tag
        if self.dico.privileged:
            self.privileged = self.dico.privileged
        else:
            self.privileged = None
        if self.dico.network_mode:
            self.network_mode = self.dico.network_mode
        else:
            self.network_mode = 'bridge'
        self.configfile = model.ConfigFile()

        self.dockerapi = docker.Client(base_url=self.configfile.docker_url,
                                       version=self.configfile.docker_version,
                                       timeout=60)
        info = self.get_info()
        self.id = info.get('id')
        self.ip = info.get('ip')
        self.hostname = info.get('hostname')
        self.started = info.get('started')
        self.created = info.get('created')


    def start(self):
        if self.started is False and self.created is True:
            print('Starting %s ...' % self.tag)

            self.dockerapi.start(container=self.id,
                                 binds=self.dico.binds,
                                 port_bindings=self.dico.port_bindings,
                                 privileged=self.privileged,
                                 network_mode=self.network_mode)
        return True

    def stop(self):
        if self.started is True:
            print('Stopping container %s ...' % self.tag)
            self.dockerapi.stop(self.id)

    def remove(self):
        self.stop()
        if self.created is True:
            print('Removing container %s ...' % self.id)
            self.dockerapi.remove_container(self.id)

    def restart(self):
        self.dockerapi.restart(self.id)

    def get_info(self):
        info = {}
        info['id'] = None
        info['ip'] = None
        info['hostname'] = None
        info['started'] = False
        info['created'] = False
        containers_list = self.dockerapi.containers(all=True)
        if containers_list:
            try:
                c_id = [item['Id'] for item in containers_list if self.tag in item['Image']][0]
            except IndexError:
                c_id = None

            if c_id:
                container_info = self.dockerapi.inspect_container(c_id)
                config = container_info['Config']
                network = container_info['NetworkSettings']
                info['id'] = c_id
                info['ip'] = network['IPAddress']
                info['hostname'] = config['Hostname']
                info['created'] = True
                if info.get('ip'):
                    info['started'] = True
        return info
