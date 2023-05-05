# Deployment of Local Containerized Relational Database using [PostgreSQL](https://kinsta.com/knowledgebase/what-is-postgresql/) & [Docker](https://www.docker.com)

<!--
```python
from IPython.display import display, HTML
display(HTML('<div style="display: flex;"> \
             <img src="Images/author_pic.jpg" alt="author profile pic" style="width:8%; \
                     border-radius:100%; border: 1px solid black;"/> \
             <div style="float: right; margin-left:3%"> \
             <p style=" font-size: 130%; margin-top:10%; ">By Stamatis Sideris</p> \
             <p style="font-size: 100%;">Updated as of: May 5, 2023</p> \
             </div> \
             </div>'))
```
-->

<div style="display: flex;">              <img src="images/author_pic.jpg" alt="author profile pic" style="width:8%;                      border-radius:100%; border: 1px solid black;"/>              <div style="float: right; margin-left:3%">              <p style=" font-size: 130%; margin-top:10%; ">By Stamatis Sideris</p>              <p style="font-size: 100%;">Updated as of: May 5, 2023</p>              </div>              </div>

-------------------------------------------------------------------------------------------------------------------------------

### Table of Contents

[1. Introduction](#introduction)

[2. Docker and Docker Compose Installation](#docker-and-docker-compose-installation)

[3. Deployment of Local PostgreSQL Database using Docker](#deployment-of-local-postgresql-database-using-docker)

[4. Conclusion](#conclusion)

### Introduction

In this tutorial, I will guide you through the process of creating a PostgreSQL ([What is PostgreSQL](https://kinsta.com/knowledgebase/what-is-postgresql/)) container using Docker ([and what is Docker](https://www.docker.com)). We will cover the basics of containerization, including setting up Docker and creating a container. We will then explore the essential components of PostgreSQL, such as creating databases, tables, and users, and how to manage them using a graphical user interface. Finally, we will deploy a container that will run PostgreSQL 

### Docker & Docker Compose Installation

Firstly, we install the docker.io in our VM instance. To do so:



```python
sudo apt-get install docker.io

docker --version
```

![image.png](attachment:image.png)

![image-2.png](attachment:image-2.png)

If we try and run docker an error occurs:

![image-3.png](attachment:image-3.png)

This happens because sudo rights are needed every time we run docker. In order to avoid running sudo each time, we add docker directory in sudo and then add our user in the directory. We activate the changes to groups with command newgrp and finally restart our instance and run docker again. Docker must be installed and ready for use.


```python
sudo groupadd docker

sudo gpasswd -a $USER docker

newgrp docker

docker run hello-world
```

![image.png](attachment:image.png)

![image-2.png](attachment:image-2.png)

![image-3.png](attachment:image-3.png)

![image-4.png](attachment:image-4.png)

Moreover, we download and install docker-compose ([link](https://github.com/docker/compose/releases)) that will help us easily manage and configure all the different containers we want to create. Firstly, create a bin directory to store your downloads. Then, visit the following link and choose the version of docker-compose you prefer for downloading. We download the docker-compose-linux-x86_64 version as our subsystem works in Ubuntu.


```python
mkdir bin

cd bin

wget {link_to_docker_compose_version} -O docker_compose
```

![image.png](attachment:image.png)

You will observe that the system does not recognize docker_compose as an executable and so we use the following command to do so.

![image-2.png](attachment:image-2.png)

Finally, in order to make the executable visible from all directories, we visit the bashrc file using nano and we add the bin directory to the path using the following line of code:

export PATH=”${HOME}/bin:${PATH}”

The bashrc file is the one storing the paths that are initialized when our instance starts. We write out the file and exit. Then, we use the source command to restart the file (we could also logout and login) and we are ready to use docker-compose.



```python
nano bashrc

source .bashrc

docker_compose version
```

![image.png](attachment:image.png)

![image-2.png](attachment:image-2.png)

![image-3.png](attachment:image-3.png)

### Deployment of Local PostgreSQL Database using Docker

We start by uploading our data to a data directory.

![image.png](attachment:image.png)

Then, we create a Docker Network. The network will enable different containers in it to communicate with each other. After we run the following command, the name of our network is displayed.


```python
docker network create pg-network
```

![image.png](attachment:image.png)

To run PostgreSQL, we create a new container based on an PostgreSQL image from Docker Hub. We define the username, password and name of our database, the path to our data, we are mapping the port to which we want to have access locally, and we set the names of the network and the image. Variable -d runs the command in detach mode. In the end we can see the name of the container that was created.


```python
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ecommerce_data" \
-v /home/stamatis/data \ 
-p 5432:5432 \
-d \ 
--network=pg-network \ 
--name pg-database \
postgres:13
```

![image.png](attachment:image.png)

To run pgAdmin, we proceed by creating another container based on a pgAdmin image from Docker Hub. We set the username and password of our user, we map the ports and we set the network and name of the container. We run again in detach mode.


```python
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
-d \
--network=pg-network \
--name pgadmin-2 \
dpage/pgadmin4
```

![image.png](attachment:image.png)

We finally forward a port to run our services locally. To do so, we choose the option PORTS in the terminal and we forward the ports 5432 and 8080 which we chose to map our services when configuring the containers.

![image-2.png](attachment:image-2.png)

We can then access pgAdmin from our browser by visiting the localhost:8080. We gain access by entering the username and password we set before.

![image-3.png](attachment:image-3.png)

Afterwards, we choose to create a new server and we give it a name. I called it “Local_Pipeline”. Finally, we create a connection to the PostgreSQL server we created in the container by passing the credentials asked.

![image-4.png](attachment:image-4.png)


Our database is ready for use!


![image-5.png](attachment:image-5.png)

### Conclusion

In conclusion, containerizing a relational database such as PostgreSQL with Docker provides several benefits, including improved portability, scalability, and simplified management. By following the steps outlined in this tutorial, you can easily create a PostgreSQL container and start exploring the capabilities of this powerful open-source database management system.
