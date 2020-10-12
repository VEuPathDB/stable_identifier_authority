import requests
"""class to interact with the OSID REST service"""


class OSIDService:
    def __init__(self, config):
        self.config = config
        self.url_base = ''

    def get_organism_id(self, organism_name):
        url = self.url_base + ''
        webservice_data = {"organismName": organism_name}
        response = requests.post(url, json=webservice_data)
        if response.status_code == requests.codes.ok:
            for organism in response.json():
                return organism[0]["organismId"]
        else:
            return False

    def get_gene_id(self, organism_id, generate_genes):
        url = self.url_base + ''
        webservice_data = {"collectionId": None, "organismId": organism_id, "generateGenes": generate_genes}
        response = requests.post(url, json=webservice_data)
        if response.status_code == requests.codes.ok:
            return response.json()["generatedIds"]
        else:
            return False

    def get_transcripts(self, transcript_patch):
        url = self.url_base + ''
        webservice_data = transcript_patch
        response = requests.post(url, json=webservice_data)
        if response.status_code == requests.codes.ok:
            return response.json()["generatedIds"]
        else:
            return False
