To run the project, you can pull the image from konnta/drf_api (main image) 
and the optional konnta/drf_app (image to be able to make calls with httpi 
for ease of use).
Alternatively, execute "docker-compose up -d --build" 
in GV_RDF/backend. You must have docker installed.

As proper documentation takes too much time for an assesment test, 
please refer to the GV_RDF/backend/gv_rdf/urls.py for the endpoints 
that have been created and how to call them (with Postman).

The existing testing units function as an example on how to build them, 
the possible testing scenarios are numerous, from the access and permissions 
of the users, to the actual testing of the implemented workflow, to use-cases 
like accepting a collaborator who showed interest in a project twice 
(this particular scenario fails in the corresponding test). 

The main app (api) is the 'gv_rdf' package. 

The package 'core' contains the logic and endpoints for user registration. 

The package 'projects; contains the logic and endpoints for project creation and 
management (like adding collaborators or user expressing interest in a project). 

Finally, the database (sqlite3) is empty, but there is a superuser with credentials [admin : 12345!@#$%]
