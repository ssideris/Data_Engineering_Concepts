## Monitoring a Flow-as-a-Code using [Prefect](https://www.prefect.io)

<!--
```python
from IPython.display import display, HTML
display(HTML('<div style="display: flex;"> \
             <img src="Images/author_pic.jpg" alt="author profile pic" style="width:8%; \
                     border-radius:100%; border: 1px solid black;"/> \
             <div style="float: right; margin-left:3%"> \
             <p style=" font-size: 130%; margin-top:10%; ">By Stamatis Sideris</p> \
             <p style="font-size: 100%;">Updated as of: August 1, 2023</p> \
             </div> \
             </div>'))
```
-->

<div style="display: flex;">              <img src="Images/author_pic.jpg" alt="author profile pic" style="width:8%;                      border-radius:100%; border: 1px solid black;"/>              <div style="float: right; margin-left:3%">              <p style=" font-size: 130%; margin-top:10%; ">By Stamatis Sideris</p>              <p style="font-size: 100%;">Updated as of: August 1, 2023</p>              </div>              </div>


### Table of Contents

[1. Introduction](#introduction)

[2. Prerequisites](#prerequisites)

[3. Creating an ETL Flow using Python](#creating-an-etl-flow-using-python)

[4. Monitoring the Flow using Prefect](#monitoring-the-flow-using-prefect)

[5. Monitoring a Containerized Flow using Prefect](#monitoring-a-containerized-flow-using-prefect)

[6. Conclusion](#conclusion)

### Introduction

Flow monitoring is about seamlessly coordinating the execution of various tasks or steps within a workflow, enabling efficient and reliable data processing pipelines. Prefect simplifies this process by providing a clean and intuitive API for defining and executing workflows. With Prefect, you can design your workflows as code, making them version-controlled, modular, and easy to maintain.

In this tutorial, we are going to use the ETL pipeline created [here](https://github.com/ssideris/Data_Management_Concepts/blob/main/DevOps/Containerized%20ETL%20Procedures%20for%20Local%20Infrastructures%20using%20Python%2C%20Docker%20%26%20Docker%20Compose/README.md#anaconda-installation) and step-by-step monitor the flow using Prefect. 

### Prerequisites

As always, I am going to start by using a VM instance provided by Google, as proposed [here](https://github.com/ssideris/Data_Management_Concepts/tree/main/DevOps/Virtual%20Machine%20Instance%20Creation%20using%20Google%20Cloud.pdf). This is a very helpful step to deal with the low specs of your computer but also, it is optional.

### Creating an ETL Flow using Python

The ETL flow-as-code to be used has been described [here](https://github.com/ssideris/Data_Management_Concepts/blob/main/DevOps/Containerized%20ETL%20Procedures%20for%20Local%20Infrastructures%20using%20Python%2C%20Docker%20%26%20Docker%20Compose/README.md#containerized-etl-procedures-for-local-infrastructures-using-python,-docker-and-docker-compose). The flow loads a Kaggle dataset using the Kaggle API and after some simple transformations, it loads it to a Postgres DB. For the parameterization of the flow, a .env file is used alongside the dotenv python library which enables us to use environment variables inside our python script. The main python script is presented below:


```python
# imports
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
import opendatasets as od
import os
# import dotenv
from dotenv import load_dotenv

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
    engine = create_engine(f'postgresql://{os.getenv("user")}:{os.getenv("password")}@{os.getenv("host")}:{os.getenv("port")}/{os.getenv("db")}')
    # append each chunk to the table - the chunk method is needed because .to_sql function cannot handle large volume of data
    df.to_sql(name=table_name, con=engine, if_exists='append')
    print("Finished ingesting data into the postgres database")

def download_data():
    od.download(os.getenv("data_url"))

def load_env():
    load_dotenv()

def log_subflow(table_name: str):
    print(f"Logging Subflow for: {table_name}")

def main_flow():
    # load environment variables
    load_env()
    # download dataset from Kaggle
    download_data()
    log_subflow(os.getenv("table_name"))
    for i in os.getenv("csv_name").split(','):
        path = os.getenv("data_path") + i
        raw_data = extract_data(path)
        data = transform_data(raw_data)
        load_data(os.getenv("table_name"), data)

if __name__ == '__main__':
    main_flow()
```

The .env file is presented below:


```python
# Parameters

# Postgres credentials
host = "pgdatabase"
port = "5432"
db = "ecommerce_data"
user = "root"
password = "root"
table_name = "ecommerce_data_all"
csv_name = "2019-Dec.csv,2019-Nov.csv,2019-Oct.csv,2020-Jan.csv,2020-Feb.csv"

# Kaggle creds
data_url = "https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop/download?datasetVersionNumber=6"
data_path = "ecommerce-events-history-in-cosmetics-shop/"
```

In order for the script to run, we need to perform some pip installations of the libraries used. As a best practise, we will create a conda environment to install the dependencies there. For anaconda installation refer [here](https://github.com/ssideris/Data_Management_Concepts/tree/main/DevOps/Containerized%20ETL%20Procedures%20for%20Local%20Infrastructures%20using%20Python%2C%20Docker%20%26%20Docker%20Compose#anaconda-installation). In order to create the virtual environment, use the following command:


```python
conda create --name ecommerce python=3.11
```

and to activate it:


```python
conda activate ecommerce
```

The requirements.txt we will use to pip install the dependencies inside the VE is the following:


```python
pandas==2.0.3
prefect==2.10.21
prefect-sqlalchemy== 0.2.4
protobuf==4.23.4
pyarrow==12.0.1
pandas-gbq==0.19.2
psycopg2-binary==2.9.6
sqlalchemy==2.0.19
opendatasets==0.1.22
python-dotenv==1.0.0
```

and the command to use inside the VE:


```python
pip install -r requirements.txt
```

As a last step, let's create a flows directory and move our python script there.


```python
mkdir flows
mv ./etl.py ./flows/etl.py
```

### Monitoring the Flow using Prefect

Prefect, uses decorators to enhance the functionality and ease of defining and managing workflows. Decorators are special functions in Python that modify the behavior of other functions or methods. Prefect has two primary decorators that are commonly used:

@task: The @task decorator is applied to functions that represent individual tasks in a Prefect workflow. These functions can be any Python code that performs a specific action or computation. When a function is decorated with @task, Prefect recognizes it as a unit of work and can track its execution, dependencies, and inputs/outputs automatically. This allows you to compose complex data pipelines by chaining tasks together, and Prefect ensures that tasks are executed in the correct order based on their dependencies.

@flow: The @flow decorator is applied to functions that represent higher-level workflows in Prefect. These functions define the entire workflow and can include multiple tasks (which may have @task decorators) and other flows. This allows you to build more complex workflows by composing smaller units of work. When a function is decorated with @flow, Prefect recognizes it as a workflow and can orchestrate the execution of tasks within the flow.

We will add a flow decorator over the main_flow function as it is the one that shows the sequence in which the tasks should be executed and then we will add a task decorator over each other function that is working as a step of the flow. Each decorator can be parameterized, setting for example a name for each task, enabling log_prints and the number of retries before failure of execution. The modified etl flow is presented below:


```python
# imports
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
import opendatasets as od
import os
# import prefect
from prefect import task, flow
# import dotenv
from dotenv import load_dotenv

@task(name="Read Data as csv", log_prints=True, retries=3)
def extract_data(path: str) :
    # read each csv in chunks of 100000 rows 
    df_iter = pd.read_csv(path, iterator=True, chunksize=100000)
    df = next(df_iter)

    return df

@task(name="Transform data", log_prints=True, retries=3)
def transform_data(df) :
    # set the datetime format and drop a table that is full of Nulls
    df['event_time'] = pd.to_datetime(df['event_time']) 
    df = df.drop('category_code', axis=1)
    return df

@task(name="Load data to PostgreSQL", log_prints=True, retries=3)
def load_data(table_name, df):
    # create an engine that connects to the postgres database
    engine = create_engine(f'postgresql://{os.getenv("user")}:{os.getenv("password")}@{os.getenv("host")}:{os.getenv("port")}/{os.getenv("db")}')
    # append each chunk to the table - the chunk method is needed because .to_sql function cannot handle large volume of data
    df.to_sql(name=table_name, con=engine, if_exists='append')
    print("Finished ingesting data into the postgres database")

@task(name="Download data from Kaggle", log_prints=True, retries=3)
def download_data():
    od.download(os.getenv("data_url"))

@task(name="Load Environment Variables", log_prints=True, retries=3)
def load_env():
    load_dotenv()

def log_subflow(table_name: str):
    print(f"Logging Subflow for: {table_name}")

@flow(name="Main Flow")
def main_flow():
    # load environment variables
    load_env()
    # download dataset from Kaggle
    download_data()
    log_subflow(os.getenv("table_name"))
    for i in os.getenv("csv_name").split(','):
        path = os.getenv("data_path") + i
        raw_data = extract_data(path)
        data = transform_data(raw_data)
        #load_data(os.getenv("table_name"), data)

if __name__ == '__main__':
    main_flow()
```

For now, we will comment out the last task of loading the data to the postgres (#load_data(os.getenv("table_name"), data)), as we have not established a connection to a postgres db yet for our flow to be able to load data there. We move on running our flow and visualizing it locally using the Prefect API and UI. To do so, first start the prefect server:


```python
prefect server start
```

then, run the flow:


```python
python ./flows/etl.py
```

and visit the provided for the UI link (The UI is running by default in port 4200):


```python
http://127.0.0.1:4200/api
```

The flow should appear in the UI, in the "Flow Runs" tab alongside information and logging about the flow and each of their tasks.

![image.png](Images/Picture2.png)

### Monitoring a Containerized Flow

Next, let's containerize our Flow using Docker and Docker Compose. If you are not familiar with Docker and Docker Compose refer [here](https://github.com/ssideris/Data_Management_Concepts/tree/main/DevOps/Deployment%20of%20Local%20Containerized%20Relational%20Database%20using%20PostgreSQL%20%26%20Docker) and [here](https://github.com/ssideris/Data_Management_Concepts/blob/main/DevOps/Containerized%20ETL%20Procedures%20for%20Local%20Infrastructures%20using%20Python%2C%20Docker%20%26%20Docker%20Compose/README.md#containerized-etl-procedures-for-local-infrastructures-using-python,-docker-and-docker-compose). The scope of the containerization is to create a network of containers that will communicate with each other. The network will host four containers. The first will pull a postgres image to use as a db for our flow data and Prefect's metadata. The second will pull an image of Pgadmin which will offer us a UI for the Postgres DB. The third will pull an image that will start the local Prefect server responsible for the Prefect API and UI. The final container will host a self-made image, using a Dockerfile, that will establish the environment and run our flow. 

To start, we firstly create the Dockerfile that will work as the blueprint for our Flow's image. The Dockerfile is pulling a Prefect image from the DockerHub that will help us connect our flow to the Prefect server and perform some deployments later on. Next, the Dockerfile is copying the local flows directory and the kaggle.json file inside the container. Pay attention to copy the kaggle.json file in the root directory so for our script to be able to read it automatically without asking us to pass the kaggle credentials. Moreover, a pip installation of all the needed libraries inside our python script is happening using the requirements.txt. Finally the command line is responsible to run our flow inside the etl.py when the image is called. 


```python
FROM prefecthq/prefect:2.10.17-python3.11

ADD flows /opt/prefect/flows

COPY kaggle.json /opt/prefect/kaggle.json 

RUN pip install -r /opt/prefect/flows/requirements.txt

CMD ["python", "/opt/prefect/flows/etl.py"]
```

We then create a docker-compose.yml file to create the network. Four services are created:

The pgdatabase is pulling a postgres 13 image to use as Database for our flow. The credentials for the server are provided as environment variables. A local data directory is mounted to the metadata of the postgres inside the container for keeping consistency. Finally, the container's port 5432 is mounted to the local port 5432 in order to access the db from outside the container.

The pgadmin is also pulling an image of the pgadmin to provide as with a UI for our postgres DB, together with some access credentials and a mounting of port 8080 to local port 80. 

The server is pulling a prefect image and starts the Prefect server using a shell script provided by the image. The environment variables provided are helping us to mount the UI and API to a url so we can access them from the browser. Moreover the variable PREFECT_SERVER_API_HOST is helping us to configure the correct host of the Docker container as it differs from the one we use locally. The variable PREFECT_API_DATABASE_CONNECTION_URL is configuring a connection to the postgres db hosted in the pgdatabase service in order to store prefect's metadata.

Finally, the etl_flow builds our image using the Dockerfile created before and runs our flow. It is important to set the environment variable PREFECT_API_URL in order for our flow to run on the prefect server started by the server service.


```python
services:
  # Postgres DB
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_HOST=pgdatabase
      - POSTGRES_DB=ecommerce_data
    volumes:
      - db:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # PGAdmin UI for Postgres
  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"

  # Prefect Server API and UI
  server:
    image: prefecthq/prefect:2.10.17-python3.11
    volumes:
      - prefect:/root/.prefect
    entrypoint:
      [
        "/opt/prefect/entrypoint.sh",
        "prefect",
        "server",
        "start"
      ]
    environment:
      - PREFECT_UI_URL=http://127.0.0.1:4200/api
      - PREFECT_API_URL=http://127.0.0.1:4200/api
      - PREFECT_SERVER_API_HOST=0.0.0.0
      - PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://root:root@pgdatabase:5432/ecommerce_data
    ports:
      - 4200:4200
    depends_on:
      - pgdatabase

  # Flow
  etl_flow:
    build: .
    image: ecommerce_etl
    working_dir: "/root/flows"
    volumes:
      - "./flows:/root/flows"
    environment:
      - PREFECT_API_URL=http://server:4200/api
    depends_on:
      - server

volumes:
  prefect:
  db:
networks:
  default:
    name: prefect-network
```

We use the following command to run the network:


```python
docker-compose up
```

The containers should start running alongside our etl flow. The loaded data can be accessed using the pgadmin UI.

![image.png](Images/Picture1.png)    

The Flow can be examined via Prefect using the following link:


```python
http://0.0.0.0:4200/api
```

![image.png](Images/Picture3.png)


### Conclusion

Overall, Prefect is a great tool for developing a flow-as-a-code and monitoring it in a simple way. From development to production, Prefect could offer its users a clear view of the steps executed inside a Flow and any points of failure. This could significantly decrease the amount of time and cost needed to develop a pipeline, making the development more independent over other software tools and more explainable to other users.
