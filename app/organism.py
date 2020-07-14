class Organism:
    def __init__(self, database_connection, production_name):
        self.production_name = production_name
        self.database_values = database_connection.load('organism', {'production_name': self.production_name},
                                                        ['organism_id', 'prefix'])
        self.organism_id = None
        if self.database_values:
            self.build = Build(database_connection, self.database_values['organism_id'])
            self.organism_id = self.database_values['organism_id']
            self.prefix = self.database_values['prefix']

    def insert_new_organism(self, database_connection, production_name, genus, species, strain, ncbi_taxonomy_id,
                            known_prefix=None):
        if self.check_uniqueness(database_connection, ('production_name', production_name)):
            # prefix = None

            if known_prefix and self.check_uniqueness(database_connection, ('prefix', known_prefix)):
                prefix = known_prefix
            else:
                prefix = self.generate_prefix(database_connection, genus, species, strain)

            organism_id = database_connection.commit('organism', {'production_name': production_name, 'genus': genus,
                                                                  'species': species, 'strain': strain,
                                                                  'ncbi_taxonomy_id': ncbi_taxonomy_id,
                                                                  'prefix': prefix})
            return organism_id
        else:
            return False

    def check_uniqueness(self, database_connection, table_value):
        table, value = table_value
        self.database_values = database_connection.load('organism', {table: value},
                                                        ['organism_id'])
        if self.database_values:
            return False
        else:
            return True

    def generate_prefix(self, database_connection, genus, species, strain):
        genus_clean = self.get_clean_letter_string(genus)
        species_clean = self.get_clean_letter_string(species)
        strain_clean = self.get_clean_letter_string(strain)

        # index is zero based
        first_letter = (genus_clean, 0)
        second_letter = (species_clean, 0)
        third_letter = (species_clean, 1)
        fourth_letter = (strain_clean, 0)

        prefix_list = [first_letter, second_letter, third_letter, fourth_letter]
        # index = 0
        prefix = self._compose_string_of_letters(prefix_list)

        while not self.check_uniqueness(database_connection, ('prefix', prefix)):
            third_string, third_index = third_letter
            fourth_string, fourth_index = fourth_letter
            if len(fourth_string) > fourth_index:
                fourth_index += 1
                prefix_list = [first_letter, second_letter, (third_string, third_index), (fourth_string, fourth_index)]
                prefix = self._compose_string_of_letters(prefix_list)
            elif len(third_string) > third_index:
                third_index += 1
                fourth_index = 0
                prefix_list = [first_letter, second_letter, (third_string, third_index), (fourth_string, fourth_index)]
                prefix = self._compose_string_of_letters(prefix_list)
            else:
                return False

        return prefix

    def _compose_string_of_letters(self, list_of_strings_with_index):

        string_of_letters = str()
        for entry in list_of_strings_with_index:
            string, index = entry
            letter = self._index_string(string, index)
            string_of_letters += letter

        return string_of_letters

    @staticmethod
    def get_clean_letter_string(string):
        letters_only = str()

        for char in string:

            if char.isalpha():
                letters_only += char

        return letters_only.upper()

    @staticmethod
    def _index_string(string, index):
        return string[index]


class Build:
    def __init__(self, database_connection, organism_id):
        self.ob_organism_id = organism_id
        self.database_values = database_connection.load('organism_build', {'ob_organism_id': organism_id}, ['build_id'])

        if self.database_values:
            self.build_id = self.database_values['build_id']

    def insert_new_build(self, database_connection, insdc_number, gene_build, status='current'):

        build_id = database_connection.commit('organism_build', {'ob_organism_id': self.ob_organism_id,
                                                                 'INSDC_number': insdc_number,
                                                                 'gene_build': gene_build, 'status': status})
        return build_id

    def update_build(self):
        pass
