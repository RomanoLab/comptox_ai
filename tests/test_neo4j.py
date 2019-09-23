from neo4j import GraphDatabase
import configparser

import pytest

CONFIG_FILE = 'CONFIG.cfg'

class TestNeo4j:
    def test_can_establish_bolt_connection(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        self.username = config['NEO4J']['Username']
        self.password = config['NEO4J']['Password']
        hostname = config['NEO4J']['Hostname']
        protocol = config['NEO4J']['Protocol']
        port = config['NEO4J']['Port']
        self.uri = "{0}://{1}:{2}".format(protocol, hostname, port)

        driver = GraphDatabase.driver(self.uri,
                                      auth=(self.username,
                                            self.password))

        session = driver.session()
        value = session.run("RETURN 1").single().value()

        assert value == 1
        driver.close()
