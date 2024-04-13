from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.storage import Filestore, GCS
from diagrams.gcp.network import LoadBalancing
from diagrams.gcp.compute import Run
from diagrams.gcp.analytics import Bigquery
from diagrams.custom import Custom
from diagrams.programming.language import Python

node_attr = {
    "fontsize": "16",
    "fontname": "Arial",
    "width": "1.3",
    "height": "1.3",
}

graph_attr = {
    "fontsize": "19",
    "pad": "0.2",
    "ranksep": "0.5",
    "nodesep": "0",
    "fontname": "Arial",
}

cluster_graph_attr = {
    "fontsize": "16",
    "pad": "0.2",
    "ranksep": "0.5",
    "nodesep": "0",
    "fontname": "Arial",
}

with Diagram("Pipeline 1", show=False, node_attr=node_attr, graph_attr=graph_attr):
    bgg = Custom("API", "./resources/bgg.png")

    with Cluster(
        "Orchestrated by Mage running on Google Cloud Run",
        graph_attr=cluster_graph_attr,
    ):
        with Cluster("1. API calls", graph_attr=cluster_graph_attr):
            api_call = Python("Python")
            filestore = Filestore("Filestore")
            raw_bucket = GCS("GCS: Raw")
        with Cluster("2. Parse XML", graph_attr=cluster_graph_attr):
            parse_xml = Python("Python")
            stage_bucket = GCS("GCS: Stage")
            bigquery_stage = Bigquery("BigQuery: Stage")

    bgg >> api_call >> [filestore, raw_bucket]
    filestore >> parse_xml >> [stage_bucket, bigquery_stage]

with Diagram("Pipeline 2", show=False, node_attr=node_attr, graph_attr=graph_attr):

    bigquery_stage = Bigquery("BigQuery: Stage")

    with Cluster(
        "Orchestrated by Mage running on Google Cloud Run",
        graph_attr=cluster_graph_attr,
    ):

        with Cluster("4. Update dbt data dictionary", graph_attr=cluster_graph_attr):
            dbt_docs = Custom("dbt", "./resources/dbt.png")
            docs_bucket = GCS("GCS: Docs")
            lb = LoadBalancing("Webpage")
        with Cluster("3. Data modelling", graph_attr=cluster_graph_attr):
            dbt = Custom("dbt", "./resources/dbt.png")
            bigquery_prod = Bigquery("BigQuery: Prod")

    bigquery_stage >> [dbt, dbt_docs]
    dbt >> bigquery_prod
    dbt_docs >> docs_bucket >> lb

with Diagram(
    "Infrastructure",
    show=False,
    node_attr=node_attr,
    graph_attr=graph_attr,
):
    with Cluster(
        "Google Cloud Platform",
        graph_attr=cluster_graph_attr,
    ):
        with Cluster("2. Terraform Mage setup", graph_attr=cluster_graph_attr):
            filestore = Filestore("Filestore")
            secrets_manager = Custom("Secret Manager", "./resources/secret_manager.png")
            with Cluster("Cloud Run", graph_attr=cluster_graph_attr):
                mage = Custom("Mage", "./resources/mage.png")
        with Cluster("1. Terraform GCS setup", graph_attr=cluster_graph_attr):
            data_bucket = GCS("Data Bucket")
            docs_bucket = GCS("Docs Bucket")
        with Cluster("3. Terraform dbt docs setup", graph_attr=cluster_graph_attr):
            lb = LoadBalancing("Load Balancer")
        bigquery = Bigquery("BigQuery")

    filestore >> Edge(label="volume mount") >> mage
    secrets_manager >> Edge(label="credentials") >> mage
    mage >> [data_bucket, docs_bucket]
    data_bucket >> bigquery
    docs_bucket >> lb
