# Databricks notebook source
# MAGIC %md
# MAGIC ## Configuration file
# MAGIC
# MAGIC Please change your catalog and schema here to run the demo on a different catalog.
# MAGIC
# MAGIC <!-- Collect usage data (view). Remove it to disable collection or disable tracker during installation. View README for more details.  -->
# MAGIC <img width="1px" src="https://ppxrzfxige.execute-api.us-west-2.amazonaws.com/v1/analytics?category=data-engineering&org_id=1172988813503077&notebook=%2Fconfig&demo_name=delta-lake&event=VIEW&path=%2F_dbdemos%2Fdata-engineering%2Fdelta-lake%2Fconfig&version=1">

# COMMAND ----------

#Note: we do not recommend to change the catalog here as it won't impact all the demo resources such as SDP pipeline and Dashboards.
#Instead, please re-install the demo with a specific catalog and schema using dbdemos.install("lakehouse-retail-c360", catalog="..", schema="...")

catalog = "main"
schema = dbName = db = "dbdemos_delta_lake"

volume_name = "delta_lake_raw_data"

# COMMAND ----------

# MAGIC %md
# MAGIC