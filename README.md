# RSG Django Template

This project is a Django-based website created by the Research Software Group. This is our template for all new Django projects.
When you make a project please mention (in a git commit?) which version of the template project you used - E.g. "Based on django-template commit 8asde872"

## Using this as a template to start up a new project

* Fork this template project (just click "fork" in GitLab)
* Change the places it talks about being a template project into your own project (e.g. name) and send a merge request to get the changes merged *in your new repository*.
* We would not normally expect you to pull any new changes from the template into your fork, or push any changes back. There may be exceptions to this though.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

#### Using virtualenv


To run this project, you're required to have the following software installed on your machine:

* Python 3 (for specific Python 3 version please see the [Django documentation](https://www.djangoproject.com/))
* pip
* virtualenv

The project dependencies are specified in requirements.txt

* cd into project directory
* create a virtualenv
* run `pip install .["lint","test"]`

#### Using Docker

* See [Docker documentation](https://docs.docker.com/)
* Ensure Docker is running
* run `docker compose build` to create the image
* run `docker compose up -d` to spawn container using the image
* visit `http://localhost:8001/` in a browser to view website
* run `docker compose down` to close container
* To access the container terminal:
    * run `docker container ls` to find CONTAINER ID
    * run `docker exec -it <CONTAINER ID> bash`

## Built With

* [Django](https://www.djangoproject.com/) - The Python web framework used

## License

See the [LICENSE.md](LICENSE.md) file for details
