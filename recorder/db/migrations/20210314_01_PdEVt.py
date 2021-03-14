"""
Initial migration
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
        CREATE TABLE websites (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            method TEXT NOT NULL,
            match_regex TEXT)
        """,
         """
         DROP TABLE IF EXISTS websites
         """),
    step("""
        CREATE TABLE websites_results (
            website_id TEXT REFERENCES websites(id),
            elapsed_time DOUBLE PRECISION,
            status INT,
            matched BOOLEAN,
            at TIMESTAMP WITHOUT TIME ZONE,

            PRIMARY KEY (website_id, at)
        )
        """,
         """
         DROP TABLE IF EXISTS websites_results
         """),
    step(
        """
        CREATE INDEX index_websites_results_on_at_desc ON websites_results(at DESC)
        """,
        """
        DROP INDEX IF EXISTS index_websites_results_on_at_desc
        """),
    step(
        """
        CREATE INDEX index_websites_results_on_at_asc ON websites_results(at ASC)
        """,
        """
        DROP INDEX IF EXISTS index_websites_results_on_at_asc
        """)
]
