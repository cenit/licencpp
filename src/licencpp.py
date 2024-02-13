#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
"""
This file is part of licencpp, which is released under the MIT License.
See file LICENSE or go to https://opensource.org/licenses/MIT for full license details.
"""

# This script reads a project's vcpkg.json file to get the project name, then uses vcpkg to generate a DGML file of the project's dependencies.
# It then reads the DGML file to extract the names of the dependencies, and reads each dependency's vcpkg.json file to extract its license.

import json
import os
import subprocess
import xml.etree.ElementTree as ET
import datetime
import yaml

# Define paths
project_vcpkg_json = 'vcpkg.json'  # Path to your project's vcpkg.json
vcpkg_ports_dir = '../vcpkg/ports'
vcpkg_executable = '..\\vcpkg\\vcpkg'  # Adjust this path to your vcpkg executable location
dependencies_dgml = 'dependencies.dgml'

# Read project's vcpkg.json to get the project name
with open(project_vcpkg_json, 'r') as file:
    project_data = json.load(file)
project_name = project_data.get('name')

# Generate dependencies.dgml file
command = f"{vcpkg_executable} depend-info --overlay-ports=. {project_name} --format=dgml > {dependencies_dgml}"
subprocess.run(command, shell=True, check=True)

# Parse the DGML file to extract dependency names
def parse_dgml(dgml_path):
    dependencies = []
    tree = ET.parse(dgml_path)
    root = tree.getroot()
    for node in root.findall('.//{http://schemas.microsoft.com/vs/2009/dgml}Node'):
        dependencies.append(node.get('Id'))
    return dependencies


def generate_spdx_document(dependencies_info):
    spdx_document = {
        "SPDXID": "SPDXRef-DOCUMENT",
        "spdxVersion": "SPDX-2.2",
        "creationInfo": {
            "created": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            "creators": ["Tool: licencpp.py 0.1.0"],
            "licenseListVersion": "3.9"
        },
        "name": "ProjectDependencyLicenseInfo",
        "dataLicense": "CC0-1.0",
        "documentNamespace": f"http://spdx.org/spdxdocs/{project_name}-{datetime.datetime.now().timestamp()}",
        "documentDescribes": [],  # List to be filled with SPDX package IDs
        "packages": []
    }

    for dep, info in dependencies_info.items():
        package_spdx_id = f"SPDXRef-Package-{dep}"
        package = {
            "name": dep,
            "SPDXID": package_spdx_id,
            "downloadLocation": info['homepage'],
            "licenseConcluded": info['license'],
            "licenseDeclared": info['license'],
        }
        spdx_document["packages"].append(package)
        spdx_document["documentDescribes"].append(
            package_spdx_id)  # Add package SPDX ID to the list

    with open("project_spdx_document.spdx.yaml", "w") as spdx_file:
        yaml.dump(spdx_document, spdx_file, sort_keys=False)

def get_license_and_homepage_from_vcpkg_json(dep_name):
    vcpkg_json_path = os.path.join(vcpkg_ports_dir, dep_name, 'vcpkg.json')
    if os.path.exists(vcpkg_json_path):
        with open(vcpkg_json_path, 'r') as file:
            dep_data = json.load(file)
        return dep_data.get('license'), dep_data.get('homepage')
    return None, None

dependencies = parse_dgml(dependencies_dgml)
dependencies_info = {}

for dep in dependencies:
    license, homepage = get_license_and_homepage_from_vcpkg_json(dep)
    if license:
        if homepage:
            dependencies_info[dep] = {'license': license, 'homepage': homepage}
        else:
            dependencies_info[dep] = {'license': license, 'homepage': 'null'}
    else:
        if homepage:
            dependencies_info[dep] = {'license': 'null', 'homepage': homepage}
        else:
            dependencies_info[dep] = {'license': 'null', 'homepage': 'null'}


generate_spdx_document(dependencies_info)
