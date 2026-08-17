# Delta Lake Learning Path

This repository contains a curated collection of scripts and tutorials designed to help you learn and master **Delta Lake**. Whether you are a beginner looking to understand the fundamentals or an experienced data engineer exploring advanced internal mechanics, these resources provide a structured path for hands-on learning.

## Repository Structure

The repository is organized into sequential modules to facilitate a progressive learning experience:

| File | Description |
| :--- | :--- |
| `00-Delta-Lake-Introduction.sql` | An overview of Delta Lake concepts and architecture. |
| `01-Getting-Started-With-Delta-Lake.sql` | Basic operations: creating, reading, and writing Delta tables. |
| `02-Delta-Lake-Performance.sql` | Optimization techniques including Z-Ordering and File Compaction. |
| `03-Delta-Lake-Uniform.py` | Working with Delta Lake UniForm (Universal Format) to enable Iceberg/Hudi compatibility. |
| `04-Delta-Lake-CDF.sql` | Implementing and using Change Data Feed (CDF). |
| `05-Advanced-Delta-Lake-Internal.sql` | Deep dive into transaction logs, checkpoints, and storage layout. |
| `config.py` | Configuration file for environment-specific settings. |

## How to Use This Repo

* **Prerequisites:** Ensure you have access to a Spark environment (like Databricks, Synapse, or a local PySpark setup) configured with the necessary Delta Lake libraries.
* **Setup:** Update `config.py` with your storage paths or database connection details.
* **Execution:** Follow the modules in numerical order to build your understanding step-by-step.
