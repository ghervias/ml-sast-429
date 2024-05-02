import logging
import unittest

from yaml import YAMLError

from mlsast.backend import connector
from mlsast.util.config import Config
from mlsast.util.helpers import get_config_path, get_docker_client

class TestSession(unittest.TestCase):
    def setUp(self):
        self.db = True
        self._logger = logging.getLogger(__name__)

        tags = []
        try:
            client = get_docker_client()
            running = client.containers.list(filters={"status": "running"})
            tags = [tag for cont in running for tag in cont.image.tags]

        finally:
            if "neo4j:latest" not in tags:
                print("Could not run database tests. Is the docker \"neo4j\" docker container up " \
                        "and running?")

                self.db = False

        self.config = None
        try:
            self.config = Config(get_config_path(prefer_home=False))

        except FileNotFoundError as e:
            self._logger.info("Failed to load config file: %s",  e)

        except YAMLError as e:
            self._logger.info("Failed to parse config file: %s", e)

        if self.db:
            print("Database container up and running. Continue testing...")


    def test_conn(self):

        """ Checks if the connection was established in the setUp function and fails if not.

        """

        if not self.db:
            self.skipTest("Database not running, skipping test.")

        try:
            with connector.Session(self.config) as sess:
                assert sess is not None

        except Exception as e:
            self._logger.info("Could not establish database connection due to exception: %s",  e)

            assert False


    def test_insert(self):

        """ Inserts two nodes into the graph database and connects both with bi-directional edges.

        """

        if not self.db:
            self.skipTest("Database not running, skipping test.")

        query = "CREATE (n:Test {type: \"testnode\"}) RETURN (n);"

        with connector.Session(self.config) as sess:
            sess.enqueue(query)
            sess.enqueue(query)
            assert len(sess) == 2

            results = sess.execute()
            assert results
            assert len(sess) == 0

        query = "MATCH (n:Test), (m:Test) " \
                "WHERE n.type = \"testnode\" " \
                "AND m.type = \"testnode\" " \
                "CREATE (n)-[r:testrel]->(m) " \
                "RETURN (n), (m);"

        with connector.Session(self.config) as sess:
            sess.enqueue(query)
            assert len(sess) == 1

            results = sess.execute()
            assert results
            assert len(sess) == 0

    def tearDown(self):
        """ Tear down method that removes all test-relationships (testrel) and -nodes (Test) from
            the database. That is, of course, if a connection was established at all to begin with.
        """

        if not self.db:
            self._logger.info("Database not running, skipping tear down.")
            return

        query = "MATCH ()-[r:testrel]->() DELETE r RETURN r;"

        with connector.Session(self.config) as sess:
            sess.enqueue(query)
            res = sess.execute()[0]

            self._logger.info("Deleted %d edges from the DB.",  len(res.relationships))

        query = "MATCH (n:Test) DELETE n RETURN n;"

        with connector.Session(self.config) as sess:
            sess.enqueue(query)
            res = sess.execute()[0]

            self._logger.info("Deleted %d nodes from the DB.",  len(res.nodes))
