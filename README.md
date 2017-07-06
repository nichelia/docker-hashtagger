Docker Hashtagger
=================

This repository is a dockerised image of a Python file hashtagger, based on Linux Ubuntu. The image is hosted on the Docker Hub and can be found [here][1].

## Technologies

Below are the main technologies used for this project. Take some time to familiarise yourself.

[Natural Language Toolkit][2]: an open source platform for analysing human language data with Python.

[Apache Tika][3]: a toolkit that detects and extracts metadata and text from over a thousand different file types.

## How to run

First, you need to install and configure Docker on your system following this [installation guide][4].

Once Docker is successfully installed and configured on your system (you should be able to run ```$ docker run hello-world```), you are ready to download a copy of this docker image.

### Downlaod local copy

Download the Docker image by using the following (replace **:version** with desired tag or empty for latest).

```bash
$ docker pull nichelia/hashtagger[:version]
```

According the docker-compose file, the image can be run as an interactive-shell for ```nltk```

#### docker-compose.yml

```yaml
nltk:
  image: nichelia/hashtagger
  command: bash
  volumes:
    - .:/code
  working_dir: /code
  restart: always
```

### Run python script

Run the image as an interactive-shell (provides an environment with all the packages required for you to run the python script).

```bash
$ docker-compose run --rm nltk
```

You first need to run Apache Tika REST API service, it will be used in the Python script for any file types appart from text [.txt]. Once in bash mode, run the following:

```bash
$ java -jar /tika-server-1.15.jar -h 0.0.0.0 &
```

Now you are ready to run the python script. It takes as a first and only parameter the directory of the files to read from. If you type the following command, it will take the sample files inlcuded in the templates folder and output the results in a text file, out.txt.

```bash
$ python hashtagger/hashtagger.py  hashtagger/templates > out.txt
```

## Clean-up

Current project will use Docker containers, images and volumes. Check out [this][5] handy cheat sheet on how to clean-up after you finished.

[1]:  https://cloud.docker.com/swarm/nichelia/repository/docker/nichelia/hastagger
[2]: http://www.nltk.org
[3]: https://tika.apache.org
[4]:  https://docs.docker.com/engine/installation
[5]: https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes