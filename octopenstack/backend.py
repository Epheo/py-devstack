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
from octopenstack import view

dockerapi = docker.Client(base_url='unix://var/run/docker.sock', version='1.12', timeout=10)

class Container(object):

    def __init__(self, service_name):
        self.view = view.View()
        self.name = service_name
        self.dico = model.Dico(self.name)

    def build(self):
        action = 'building'
        quiet = False
        rm = False
        stream = False
        timeout = None
        custom_context = False
        fileobj = None

        self.view.service_information(action,
                                      self.dico.name,
                                      self.dico.tag,
                                      self.dico.path,
                                      self.dico.nocache)

        for line in dockerapi.build(self.dico.path,
                                    self.dico.tag,
                                    quiet, 
                                    fileobj, 
                                    self.dico.nocache,
                                    rm, 
                                    stream, 
                                    timeout, 
                                    custom_context):
            self.view.display_stream(line)

    def create(self):
        action = 'creating'
        command = None
        user = 'root'
        mem_limit = '0'
        hostname = self.name
        detach = False

        self.view.service_information(action,
                                      self.dico.tag,
                                      command,
                                      hostname,
                                      user,
                                      ports,
                                      mem_limit,
                                      self.dico.config,
                                      volumes,
                                      name)
        
        id_container = dockerapi.create_container(tag, 
                                                  command,
                                                  hostname,
                                                  user,
                                                  detach,
                                                  ports,
                                                  environment,
                                                  volumes,
                                                  name)
        return id_container

    def start(self):
        action = 'starting'
        publish_all_ports = True

        self.view.service_information(action,
                                      id_container,
                                      port_bindings,
                                      privileged)
        dockerapi.start(id_container,
                        binds,
                        port_bindings,
                        publish_all_ports)
    
    def stop(self, tag, rm):
        launched_containers = self.get_info(tag)
        if bool(launched_containers) is True:
            containers = launched_containers.keys()
            for container in containers:
                container_infos = launched_containers.get(container)
                dockerid = container_infos.get('dockerid')
                self.view.stopping(tag)
                timeout = 30
                dockerapi.stop(dockerid, timeout)
                if rm is True:
                    self.view.removing(tag)
                    dockerapi.remove_container(dockerid)
                else:
                    pass
        else:
            self.view.notlaunched(tag)

        return launched_containers

    def get_info(self, tag):
        containers_list = dockerapi.containers()
        launched_containers = {}

        for containers in containers_list:
            c_id = containers.get('Id')
            container_infos = dockerapi.inspect_container(c_id)

            config = container_infos.get('Config')
            if config.get('Image')==tag:
                network = container_infos.get('NetworkSettings')

                container_specs = {}
                container_specs['ipaddr'] = network.get('IPAddress')
                container_specs['dockerid'] = c_id
                container_specs['hostname'] = config.get('Hostname')

                launched_containers[tag] = container_specs

        return launched_containers

        # Retrieve existing containers informations:
        # """"""""""""""""""""""""""""""""""""""""""
        # First  retrieve all  the instances IDs, 
        # Get informations  for  the returned IDs 
        # And check for a match with a known tag.
        #
        # Then get instances  informations in the 
        # dictionary for the matching one.
        #
        # Returned informations are stored in the 
        # 'launched_containers' dictionary.

    def get_ip(self, tag):
        launched_containers = self.get_info(tag)

        ip_list = []

        if bool(launched_containers)==True:
            containers = launched_containers.keys()

            for container in containers:
                container_infos = launched_containers.get(container)
                ipaddr = container_infos.get('ipaddr')

                ip_list.append(ipaddr)
                self.view.ip(tag, ipaddr)
        else:
            self.view.notlaunched(tag)

        return ip_list