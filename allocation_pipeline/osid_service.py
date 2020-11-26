"""
Copyright [2019-2020] EMBL-European Bioinformatics Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests
"""class to interact with the OSID REST service"""


class OSIDService:
    def __init__(self, config):
        self.config = config
        self.url_base = self.config['OSID']['url']
        self.user = self.config['OSID']['user']
        self.password = self.config['OSID']['pass']

    def get_organism_id(self, organism_name):
        url = self.url_base + 'organisms'
        webservice_data = {"organismName": organism_name}
        response = requests.get(url, params=webservice_data, auth=(self.user, self.password))
        if response.status_code == requests.codes.ok:
            return response.json()[0]["organismId"]
        else:
            print(response.text)
            return False

    def get_gene_id(self, organism_id, generate_genes):
        url = self.url_base + 'idSets'
        webservice_data = {"collectionId": 1, "organismId": organism_id, "generateGenes": generate_genes}
        response = requests.post(url, auth=(self.user, self.password), json=webservice_data)
        if response.status_code == requests.codes.ok:
            return response.json()["idSetId"], response.json()["generatedIds"]
        else:
            print(response.text)
            return False

    def get_transcripts(self, id_set_id, transcript_patch):
        url = self.url_base + 'idSets/' + str(id_set_id)
        webservice_data = transcript_patch
        response = requests.patch(url, auth=(self.user, self.password), json=webservice_data)
        if response.status_code == requests.codes.ok:
            result = requests.get(url, auth=(self.user, self.password))
            if result.status_code == requests.codes.ok:
                return result.json()["generatedIds"]
            else:
                print(result.text)
                return False
        else:
            print(response.text)
            return False
