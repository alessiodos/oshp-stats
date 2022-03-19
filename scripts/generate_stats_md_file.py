#!/usr/bin/python3
"""
Script using the gathered data to generate/update a markdown file with mermaid pie charts with differents statistics about HTTP security headers usage.

Mermaid was used because GitHub support mermaid syntax in markdown file.

Source:
    https://mermaid-js.github.io/mermaid/#/pie
"""
import sqlite3
from datetime import datetime
from oshp_headers import OSHP_SECURITY_HEADERS

# Constants
DATA_FOLDER = "../data"
DATA_DB_FILE = f"{DATA_FOLDER}/data.db"
MD_FILE = f"../stats.md"
SECTION_TEMPLATE = """
## %s

%s

```mermaid
%s
```
"""

# Utility functions


def execute_query_against_data_db(sql_query):
    with sqlite3.connect(DATA_DB_FILE) as connection:
        curs = connection.cursor()
        curs.execute(sql_query)
        records = curs.fetchall()
        return records


def add_stats_section(title, description, chart_mermaid_code):
    with open(MD_FILE, mode="a", encoding="utf-8") as f:
        md_code = SECTION_TEMPLATE % (title, description, chart_mermaid_code)
        f.write(f"{md_code}\n")


def init_stats_file():
    with open(MD_FILE, mode="w", encoding="utf-8") as f:
        cdate = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
        f.write(f"# Statistics\n")
        f.write(
            f"> :timer_clock: Last update: {cdate} - Domains analyzed count: {get_domains_count()}.\n")


def get_domains_count():
    return len(execute_query_against_data_db("select distinct domain from stats"))


def get_pie_chart_code(title, dataset_tuples):
    #code = f"pie title {title}\n"
    code = f"pie\n"
    for dataset_tuple in dataset_tuples:
        code += f"\t\"{dataset_tuple[0]}\" : {round(dataset_tuple[1],2)}\n"
    return code


# Functions in charge of generate stats sections


def compute_header_global_usage(header_name):
    title = f"Global usage of header '{header_name}'"
    description = f"Provide the distribution of usage of the header '{header_name}' across all domains analyzed."
    # Prevent the case in which a domain specify X times the same headers...
    query = f"select distinct domain from stats where lower(http_header_name) = '{header_name}'"
    count_of_domains_using_the_header = len(
        execute_query_against_data_db(query))
    domains_count = get_domains_count()
    percentage_of_domains_using_the_header = (
        count_of_domains_using_the_header * 100) / domains_count
    dataset_tuples = [("Using it", percentage_of_domains_using_the_header),
                      ("Not using it", (100-percentage_of_domains_using_the_header))]
    pie_chart_code = get_pie_chart_code(title, dataset_tuples)
    add_stats_section(title, description, pie_chart_code)


def compute_insecure_framing_configuration_global_usage():
    header_name = "x-frame-options"
    title = f"Global usage of insecure framing configuration via the header '{header_name}'"
    description = f"Provide the distribution of usage of the header '{header_name}' across all domains analyzed with a insecure framing configuration: value different from DENY or SAMEORIGIN including unsupported values."
    query = f"select count(*) from stats where lower(http_header_name) = '{header_name}' and lower(http_header_value) not in ('deny','sameorigin')"
    count_of_domains = execute_query_against_data_db(query)[0][0]
    domains_count = get_domains_count()
    percentage_of_domains = (count_of_domains * 100) / domains_count
    dataset_tuples = [("Insecure conf", percentage_of_domains),
                      ("Secure conf", (100-percentage_of_domains))]
    pie_chart_code = get_pie_chart_code(title, dataset_tuples)
    add_stats_section(title, description, pie_chart_code)


def compute_hsts_preload_global_usage():
    header_name = "strict-transport-security"
    title = "Global usage of the Strict Transport Security 'preload' feature"
    description = f"Provide the distribution of usage of the '[preload](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security#preloading_strict_transport_security)' feature for the header '{header_name}' across all domains analyzed."
    query = f"select count(*) from stats where lower(http_header_name) = '{header_name}' and lower(http_header_value) not like '%preload%'"
    count_of_domains = execute_query_against_data_db(query)[0][0]
    domains_count = get_domains_count()
    percentage_of_domains = (count_of_domains * 100) / domains_count
    dataset_tuples = [("Using it", percentage_of_domains),
                      ("Not using it", (100-percentage_of_domains))]
    pie_chart_code = get_pie_chart_code(title, dataset_tuples)
    add_stats_section(title, description, pie_chart_code)


if __name__ == "__main__":
    init_stats_file()
    for header_name in OSHP_SECURITY_HEADERS:
        compute_header_global_usage(header_name)
    compute_insecure_framing_configuration_global_usage()
    compute_hsts_preload_global_usage()
