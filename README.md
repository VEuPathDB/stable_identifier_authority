# The assignment and tracking of stable identifiers in the VEupathDB project.


## Project description
All new gene, transcript and translation stable identifiers must be generated by the OSID webservices and changes tracked in the production session service database.

### Features
When gene models are created the must be assigned a stable identifier and if the new gene model arise from a split or merge of exsisting gene models a history of the stable identifiers must be kept so that the new gene models can be tracked back to the original gene models. Gene models that was edited should not have new stable IDs but the occurrence must be recorded in the history file to track version.   

The allocation service can extraxt gene model event information from the output of gene_model_diff and using OSID update a corresponding GFF file with new stable IDs, in addition it will write the stable IDs history to a flat file. The OSID webservice is responsable for generating new stable IDs. The session service databse is responsable for recording which pipelines created and deleted stable IDs in the core databases. The event_input and event_output modules can be extented to include gene model changes from other pipelines.

### Usage
To setup the allocation service each organsim needs a allocation_pipeline.conf. The session_service.conf needs connection infromation for the session service database. 

####To run the software:

  python3 run_allocation_pipeline.py

* schema: The database schema for the session service database.
 
