# Containerized ETL Procedures for Local Infrastructures using Python, Docker & Docker Compose

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

<div style="display: flex;">              <img src="Images/author_pic.jpg" alt="author profile pic" style="width:8%;                      border-radius:100%; border: 1px solid black;"/>              <div style="float: right; margin-left:3%">              <p style=" font-size: 130%; margin-top:10%; ">By Stamatis Sideris</p>              <p style="font-size: 100%;">Updated as of: May 5, 2023</p>              </div>              </div>


-------------------------------------------------------------------------------------------------------------------------------

### Table of Contents

[1. Introduction](#introduction)

[2. Tech Stack](#tech-stack)

[3. Anaconda Installation](#anaconda-installation)

[4. Docker and Docker Compose Installations](#docker-and-docker-compose-installations)

[5. Conainerized ETL Procedures for Local Infrastructures using Python, Docker and Docker Compose](#containerized-etl-procedures-for-local-infrastructures-using-python,-docker-and-docker-compose)

[6. Conclusion](#conclusion)

### Introduction

ETL is a process that involves extracting data from various sources, transforming it into a useful format, and loading it into a target system. However, setting up an ETL infrastructure can be a daunting task, especially for small-scale businesses or individual developers. That's where containerization comes in handy. By using Docker and Docker Compose, you can easily package your ETL processes into a container that can be run on any machine with Docker installed, without worrying about the dependencies and setup. Python is doing all the rest.

### Tech Stack

Python, Docker, Docker Compose, PostgreSQL

### Anaconda Installation

We install Anaconda as it includes Python 3.9 which we need to run in Terminal.
Visit the [link](https://www.anaconda.com/download) and choose the installer that fits your OS. I choose the Linux Installer.

![image.png](attachment:image.png)

Download it with the wget command in your terminal. 


```python
wget {the link to the anaconda release}
```

![image.png](attachment:image.png)

Install it with the bash command and choose to initialize it. Restart your terminal and Anaconda should be ready to run!


```python
bash {the downloaded file}

conda --version
```

![image.png](attachment:image.png)

![image-2.png](attachment:image-2.png)

### Docker and Docker Compose Installations

Please refer to [this tutorial](https://github.com/ssideris/Data_Engineering_Concepts/tree/main/Deployment%20of%20Local%20Containerized%20Relational%20Database%20using%20PostgreSQL%20%26%20Docker) for the installations.

###  Conainerized ETL Procedures for Local Infrastructures using Python, Docker and Docker Compose

We will use Python to create a very basic ETL flow that will extract, transform and load our data from the local data folder to the PostgreSQL database. The whole procedure will run inside a Docker network which will allow us to test our procedures without the risk of affecting the underlying infrastructure.

Firstly, we proceed by creating a local folder called “local_flow” where we will store our ETL flow. Inside the directory, we create an etl directory to store our ETL procedures. Inside the etl directory, we create a etl.py python file, which we will use to perform the ETL procedures, and a constants.py python file where we will set the parameters needed for our flow.



```python
mkdir local_flow

mkdir local_flow/etl
```

Inside the etl directory, we create a parameters.py python file where we will set the parameters needed for our flow


```python
# Parameters
host = "pgdatabase"
port = "5432"
db = "ecommerce_data"
table_name = "ecommerce_data_all"
csv_name = ["2019-Dec.csv","2019-Nov.csv","2019-Oct.csv","2020-Jan.csv","2020-Feb.csv"]
data_url = "https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop/download?datasetVersionNumber=6"
data_path = "ecommerce-events-history-in-cosmetics-shop/" 	

```

Moreover, we procceed by creating a etl.py file which we will use to perform the ETL procedures. The file performs very basic transformation on the data and loads them at the PostgreSQL Database inside the Docker. To create a Docker container that hosts PostgreSQL Database refer [here](https://github.com/ssideris/Data_Engineering_Concepts/tree/main/Deployment%20of%20Local%20Containerized%20Relational%20Database%20using%20PostgreSQL%20%26%20Docker).


```python
# imports
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
# import the parameters.py
import parameters
import opendatasets as od

def extract_data(path: str) :
    # read each csv in chunks of 100000 rows
    df_iter = pd.read_csv(path, iterator=True, chunksize=100000)
    df = next(df_iter)

    return df

def transform_data(df) :
    # set the datetime format and drop a table that is full of Nulls
    df['event_time'] = pd.to_datetime(df['event_time'])
    df = df.drop('category_code', axis=1)
    return df

def load_data(table_name, df):
    # create an engine that connects to the postgres database
    engine = create_engine(f'postgresql://{constants.user}:{constants.password}@{constants.host}:{constants.port}/{constants.db}')
    # append each chunk to the table - the chunk method is needed because .to_sql function cannot handle large volume of data
    df.to_sql(name=table_name, con=engine, if_exists='append')
    print("Finished ingesting data into the postgres database")    

def log_subflow(table_name: str):
    print(f"Logging Subflow for: {table_name}")

def main_flow():
    # download dataset from Kaggle
    od.download(constants.data_url)
    log_subflow(constants.table_name)
    for i in constants.csv_name:
        path = constants.data_path + i
        raw_data = extract_data(path)
        data = transform_data(raw_data)
        load_data(constants.table_name, data)

if __name__ == '__main__':
    main_flow()

```

As a result, our database should be loaded with our transformed data. To test it, we run a Select statement in postgres using pgadmin. For pgadmin configuration refer [here](https://github.com/ssideris/Data_Engineering_Concepts/tree/main/Deployment%20of%20Local%20Containerized%20Relational%20Database%20using%20PostgreSQL%20%26%20Docker).

![image.png](attachment:image.png)

We create a Docker image called “ecommerce_data_local_flow”, to use it as a blueprint on creating the container that will run the etl.py and constants.py .

In order to apply our flow to the containerized network, we visit our local_flow directory and create a Dockerfile. In the Dockerfile we set what we want our image to include, which is to install the libraries needed in the python scripts, the python scripts and the data to be used.



```python
FROM python:3.9.1

RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY etl.py etl.py
COPY parameters.py parameters.py
COPY data.zip data.zip

ENTRYPOINT ["python", "etl.py", "parameters.py"]
```

![image.png](attachment:image.png)

We then proceed on creating the image.


```python
docker build -t ecommerce_data_local_flow .
```

![image.png](attachment:image.png)

We proceed to create the container that will run our ETL procedure via Docker.


```python
docker run -it --network=pg-network ecommerce_data_local_flow
```

![image.png](attachment:image.png)

Back to pgAdmin and our table must be loaded with our data!

![image-2.png](attachment:image-2.png)

The whole procedure could become much faster and maintainable by using Docker Compose. Docker Compose will use a .yaml file, where we will configure our services, to create the network that will host our services. The file would have the following structure:


```python
services:
    pgdatabase:
        image: postgres:13
        environment:
            - POSTGRES_USER=root
            - POSTGRES_PASSWORD=root
            - POSTGRES_DB=ecommerce_data
        volumes:
            - "./data:/var/lib/postgresql/data:rw"
        ports:
            - "5432:5432"
    pgadmin:
        image: dpage/pgadmin4
        environment:
            - PGADMIN_DEFAULT_EMAIL=admin@admin.com
            - PGADMIN_DEFAULT_PASSWORD=root
        ports:
            - "808:80"
    local_etl_flow:
        build:.
        image:local_etl_flow
        stdin_open: true
        tty: true
        volumes:
            - .:/ecommerce_data
```

![image.png](attachment:image.png)

We configure three services, the pgdatabase which will use the image postgres:13 from Docker Hub to create a pgdatabase container, the pgadmin which will use the image dpage/pgadmin4 from Docker Hub to create a pgadmin container and the local_etl_flow which will search for and use our Dockerfile to create a local_etl_flow container. All the containers will run under the same network.

Before running the Docker Compose, firstly remove all the existing images from docker. We do this because images already exist from our previous manual trial without Docker Compose and they take storage space. To do so:


```python
docker images rmi
```

![image.png](attachment:image.png)

Then, to run Docker Compose, use the following command:


```python
docker_compose up -d
```

![image.png](attachment:image.png)

All 3 containers are running. To check them, we use the following command:


```python
docker ps
```

![image.png](attachment:image.png)

Next step, we need to enter to our local_etl_flow container to access the directory installed in it and run our etl.py file. To do so:


```python
docker exec -it loacl_flow-local_etl_flow-1 bash
```

![image.png](attachment:image.png)

After the script is finished running, we visit again the pgadmin in localhost port 80 and register our postgres database in host pgdatabase. The database should exist and include a table “ecommerce_data_all” filled with our data.

![image-2.png](attachment:image-2.png)

Use the following command to close all the running containers:


```python
docker compose down
```

![image.png](attachment:image.png)

### Conclusion

In conclusion, containerizing your ETL procedures using Python, Docker, and Docker Compose is a great way to simplify the deployment process, improve portability, and ensure consistency across different environments. By following the steps outlined in this tutorial, you should be able to create a containerized ETL infrastructure for your local development or testing environment, and easily scale it up as needed.
