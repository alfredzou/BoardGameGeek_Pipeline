# BoardGameGeek Pipeline

### What is BoardGameGeek?
​BoardGameGeek (BGG) is a popular online forum for board game hobbyists and a database of 121k board games and 33k expansions. BGG's database serves as one of the most comprehensive and current board game datasets, allowing for interesting analysis on board gaming trends and user preferences. 

![](./documentation/resources/bgg_api_logo.webp)

### Links

- [**Design Decisions**](#Design-Decisions) - Detailed explanation of choice of methodology, infrastructure and tools
- [Set up instructions](terraform/setup.md) - Instructions to run the pipeline yourself
- [dbt docs](https://alfredzou.github.io/#!/overview) - dbt documentation
- [BoardGameGeek Analysis](https://lookerstudio.google.com/s/s2s628UzcQk) - Analysis performed on collected data

### Pipeline Introduction

This pipeline extracts BGG's XML API2 data, parses the XML files and saves the denormalised data into a BigQuery staging schema. Data is modelled into a star schema using dbt and saved into a daily table in the production schema. This data is then incrementally loaded into respective historical tables in the production schema.

<img src="./documentation/pipeline.png" alt="pipeline" width="800"/>

### Infrastructure Introduction

Google Cloud Platform is being used as the cloud provider. All infrastructure is set up is through terraform files. Minimal configuration of terraform variables files are required for project id and bucket names. [Set up instructions](terraform/setup.md)

- The main infrastructure setup is Cloud Run running Mage containers with 2 vCPUs and 4 GBs of memory. Filestore volumes are mounted to Mage to provide a local filesystem. The service account keys, stored in Secret Manager, are also mounted to Filestore for Mage's access. 

- A data bucket is used for storing raw and staged data. BigQuery is used as an OLAP database.

- The document bucket holds the dbt data dictionary, which is accessible through the load balancer. [dbt docs](https://alfredzou.github.io/#!/overview)

<img src="./documentation/infrastructure.png" alt="infrastructure" width="700"/>

### Tools & Technologies
- Infrastructure as code: Terraform
- Orchestrator: Mage
- Cloud storage: Google Cloud Storage
- Cloud database: BigQuery
- Cloud compute: Cloud Run
- Transformations: dbt
- Language: Python
- Dashboard: Looker

# Design Decisions

In this postmortem, I reflect on the decisions made regarding the pipeline and infrastructure, highlighting what worked well, what didn't go as planned, and any unexpected challenges encountered along the way.

## Contents
- [Pipeline Design Explanation](#Pipeline-Design-Explanation)
- [Infrastructure Design Explanation](#Infrastructure-Design-Explanation)
- [Tools & Technologies Design Explanation](#Tools-&-Technologies-Design-Explanation)

## Pipeline Design Explanation

The process is broken up into 4 steps:
1. Make ~170 API calls to retrieve and save the XML data locally. The XML data is then uploaded to the 'Raw' folder in a Google Cloud Storage (GCS) bucket.
2. The XML data is parsed for relevant fields. Parsed data is loaded to BigQuery 'Stage' schema, and parquet files are uploaded to the 'Stage' folder in a GCS bucket. 
3. Stage data is normalised and modelled into a Star Schema. This data is loaded in the 'Production' schema. After the daily load is complete, this is incrementally loaded into the relevant history tables in the 'Production' schema.
4. The dbt documentation is generated and uploaded to the documents bucket. This is viewable through a url provided by the http load balancer.

<img src="./documentation/pipeline.png" alt="pipeline" width="800"/>

## Specific Design Decisions
- [Minimise API calls](#minimise-API-calls)
- [API call reliability](#reliability) - retrying, error handling, logging, failing loudly and testing
- [Idempotent](#Idempotent)
- [Chunking](#Chunking)
- [Separation of extraction and transformation](#Separation-of-extraction-and-transformation)
- [No Partitioning or Clustering](#No-Partitioning-or-Clustering)
- stores raw data
- orchestrated

### Minimise API calls

API calls are a significant speed bottleneck for the pipeline. Efforts have been made to minimise the number of API calls, whilst providing a 10 second wait time to reduce the impact on the public API. 
- Currently the natural id goes up to ~420k, which would mean 420k API calls
- The first optimisation was querying multiple ids per API call. From testing, 900 ids per call would reliably not trigger the 414 error of URI is too long. This brings the number of API calls down to ~460
- The next optimisating was downloading the daily id list. There are gaps in the natural ids, cutting the number of ids to be searched to ~150k. This further reduces the number of API calls to ~170

This pipeline currently takes about 2 hours to run, with ~170 API calls taking around 1 hour and 40 minutes.

### API call reliability: retrying, error handling, logging, failing loudly and testing <a id="reliability"></a>

Given that the API call process takes so long, it's important to make sure the process is fault tolerant.
- The first method, is retrying 5 more times if the API call request returns 429 (Too many requests), 502 (Bad gateway) or 503 (Service Unavailable). Successive retry attempts are made after a 1, 2, 4, 8 and 16 second delay.
``` python
with requests.Session() as s:
    retries = Retry(total=5, backoff_factor=2, 
            status_forcelist=[429, 502, 503], allowed_methods=["GET"])
    s.mount('https://', HTTPAdapter(max_retries=retries))
```
- The second method, involves the Try Except Raise pattern. In the try method, it attempts to make an API call. If this fails the Except block will log and re-raise the error. Logging gives visibility on why the API call failed for debugging, whilst re-raising the error allows the pipeline to fail loudly. Failing loudly is important, to prevent erroneous data being served to stakeholders.
- Additionally, the Except block allows handling of specific errors such as Chunked Encoding Error. This error occurs when receiving improperly formatted chunked data from a http request. When a Chunked Encoding Error occurs, the code below will retry up to 3 times with a 10 second delay.
``` python
max_chunking_retries = 3
api_wait = 10

for retry_count in range(1, max_chunking_retries+1):
    try:
        r = s.get(url, params=params)
        r.raise_for_status()
        
        with open(raw_file_path, 'wb') as f:
            for row in r:
                f.write(row) 
        break
    except ChunkedEncodingError as e:
        logging.warning(f"An error occurred with api call {i}", exc_info=True)
        if retry_count <= max_chunking_retries:
            logging.warning(f"Retrying API call {i} after {api_wait} seconds...")
            sleep(api_wait)
        else:
            logging.error(f"Maximum retry attempts reached for API call {i}", 
            exc_info=True)
            raise
    except Exception as e:
        logging.error(f"An error occurred with api call {i}", exc_info=True)
        raise
```
- Unfortunately due to project scope, I wasn't able to write tests to improve the reliability of API call code. Especially since API calls are so variable, I would of used mocking to test handling of edge cases. Furthermore, CI/CD could of been set up using github actions to automatically test new code when it is pushed to the repository.

### Idempotent

When an error occurs with a pipeline run, we want to be able to recover from partial executions. Idempotence is the property of an operation where running it multiple times will have the same effect of running it once.
- One example of this is using a delete create pattern. The below code involves deleting folders created and recreating them.
``` python
def recreate_folders(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return None
```
- Another example of this is using a replace file pattern. Most of the code to upload to GCS or BigQuery will overwrite existing files. Although, this method isn't as full proof as the delete create pattern.
- One key pipeline process is incrementing the daily data into respective history tables in the 'production' schema. To avoid data duplication and ensure idempotence, the data is incrementally loaded based on unique key. If that unique key already exists in the history table, that row of data will not be inserted.
``` sql
{{
    config(
        materialized='incremental',
        unique_key=['date','bgg_id'],
        incremental_strategy="merge",
        on_schema_change='fail'
    )
}}
```

### Chunking

Since cloud computing is often continuously run for scheduling of pipeline jobs, it's important to make sure the code is memory efficient. This is to reduce costs on cloud computing infrastructure. To achieve this chunking is used consistently to remove memory usage.

Pandas is notoriously known for not being memory efficient, so it would be interesting to see if packages like Polars, Dask, Modin and DuckDB will be better suited.

### Separation of extraction and transformation

A key idea of this pipeline is the separation of extraction and transformation processes into two separate pipelines.
- The first pipeline would extract the API data, as this pipeline would be based on the run date. This pipeline would then save the raw XML data to a GCS bucket. This follows a ELT framework. Since storage is cheap, with compute being expensive, its 


<img src="./documentation/screenshots/mage_dag_1.png" alt="mage_dag_1" width="400"/>
<img src="./documentation/screenshots/mage_dag_2.png" alt="mage_dag_2" width="290"/>

### Daily staging tables



The raw and staged data is stored based on execution date (Sydney time) in a 'Year/Month/Day' folder structure in the GCS under `Year/Month/Day/raw_data` and `Year/Month/Day/stage_data` folders respectively. Similarly the BigQuery daily staging table are stored in a similar format if `bgg-YYYY-MM-DD` and `sp-YYYY-MM-DD`.

This is to make the data more resilient to upstream changes


### Data is easy to use


### Partitioning and Clustering

Due to the small daily data size of ~150,000 rows, partitioning and clustering of the history table was not used. It's likely that partitioning and clustering a small dataset will actually reduce the query speed with excess metadata.

### Automated documentation

Another key idea is automating the 


## Infrastructure Design Explanation

The aim was to design a pipeline that is easy to setup and repeatable.

I wanted to simulate a professional setup opposed to 

<img src="./documentation/infrastructure.png" alt="infrastructure" width="700"/>

### Design Principles
- Infrastructure as code
- Version controlled
- Simulate professional setup
- Functionally separate
- Orchestrated

## Infrastructure Decisions

#### Orchestrator

The orchestrator is one of the most important 

#### Automated deployment of docs

<img src="./documentation/screenshots/dbt_lineage.png" alt="dbt_lineage" width="900"/>

## Tools & Technologies Design Explanation
- Infrastructure as code: Terraform
- Orchestrator: Mage
- Cloud storage: Google Cloud Storage
- Cloud database: BigQuery
- Cloud compute: Cloud Run
- Transformations: dbt
- Language: Python
- Dashboard: Looker

### Infrastructure as code



### Orchestrator

An orchestrator is important to manage our pipeline runs . Mage was picked, as I was familiar with it.



### Cloud compute - Cloud Run vs Virtual Machine

There were two options for deploying Mage.
- A cheaper setup would be deploying Mage on a virtual machine. The cost would roughly be $30 per month for 2 vCPU and 4 GBs of memory and another $10 per month for 100 GBs of storage. The downside of this would require more management overhead.
- As I was trying to simulate a more professional environment, I decided to deploy Mage using Cloud Run connected to Filestore, a managed filesystem. This is an expensive option, see below. Filestore's minimum size is 1Tb and costs $10 per day, whilst running Cloud Run daily can cost $8 per day for a 2 vCPU and 4 GBs of memory. The biggest benefit of using serverless compute is reducing the management overhead and providing the ability to easily scale horizontally by creating new containers.

<img src="./documentation/screenshots/costs.png" alt="cost" width="500"/>

### Cloud database - OLAP vs OLTP

An OLAP database was chosen over an OLTP database, as the resulting data is being used for analytical use. An OLAP database is more efficient for analytics, as the data is columnar stored. Performing an aggregation, would not require scanning the entire table. BigQuery was chosen as it is GCP's OLAP database.

### Transformations - dbt vs PySpark

Since the dataset was small, there was no need to use the parallel processing of PySpark. Additionally there would of been a lot of additional infrastructure overhead of setting up a spark cluster using Dataproc, Google's managed Spark cluster.

Additionally there are a lot of benefits for using dbt:
- it's easy to write tests
- leverages the compute of a database
- generates data dictionary
