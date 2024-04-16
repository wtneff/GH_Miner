import pytest
from selenium import webdriver
import mysql.connector
import docker
import subprocess
import os
import time
import yaml
from tempfile import mkdtemp
from shutil import rmtree
from pathlib import Path

CLIENT = docker.from_env()
TMP_DIR = mkdtemp()
ROOT_DIR = Path(__file__).parents[2].resolve()

def get_docker_client():
    return CLIENT

def setup_database():
    subprocess.run(['docker', 'compose', 'exec', 'ghminer', 'flask', 'db', 'upgrade'])
    subprocess.run(['docker', 'compose', 'exec', 'ghminer', 'python', '-m', 'backend.scripts.seed_db'])

class IntegrationTests: 
    

    DOCKER_FILES = pytest.mark.datafiles(
            ROOT_DIR / 'Dockerfile',
            ROOT_DIR / 'docker-compose.yml',
    )

    @classmethod
    def setup_class(cls):
        """Stands up the test environment"""
        with open(f'{ROOT_DIR}/docker-compose.yml', 'r') as file:
            compose_file = yaml.safe_load(file)
            compose_file['services']['mysql']['volumes'] = [f'{TMP_DIR}/data:/var/lib/mysql']
            del compose_file['services']['mysql']['volumes']

        file = open(f'{TMP_DIR}/test-compose.yml', 'w')
        file.write(yaml.dump(compose_file))
        file.close()

        print(f'TMP_DIR: {TMP_DIR}')
        subprocess.run(['docker', 'compose', '-f', f'{TMP_DIR}/test-compose.yml', 'up', '--wait'], stdout=subprocess.PIPE)
        client = get_docker_client()
        container = client.containers.get('my-mysql-container')
        logs = container.logs(stream=True)
        for line in logs:
            print(line.strip())
            if "Plugin ready for connections. Bind-address: '::' port: 33060, socket" in str(line):
                logs.close()     
        setup_database()


    @classmethod
    def teardown_class(cls):
        """Tears down the test environment"""
        subprocess.run(['docker', 'compose', '-f', f'{TMP_DIR}/test-compose.yml', 'rm', '-s', '--force'])
        rmtree(TMP_DIR)


    @DOCKER_FILES
    def test_dockerfiles_exist(self, datafiles):
        """Test that the Dockerfile and docker-compose.yml file exist in the root directory"""
        for file in datafiles.iterdir():
            assert os.path.exists(file)

    def test_containers_exist(self):
        """Gets the names of the running containers and asserts they are what is expected"""
        client = get_docker_client()
        containers = client.containers.list()
        container_names = ["ghminer", "my-mysql-container"]
        for container in containers:
            assert container.name in container_names

    def test_database_connection(self):
        """Tests the connection to the database"""
        with open(f'{TMP_DIR}/test-compose.yml', 'r') as file:
            compose_file = yaml.safe_load(file)
    
        sql_environment = compose_file['services']['mysql']['environment']
        connection = mysql.connector.connect(
            host="0.0.0.0",
            port=3306,
            user="root",
            password=sql_environment['MYSQL_ROOT_PASSWORD'],
            )
        
        cursor = connection.cursor()
        cursor.execute("SELECT user FROM mysql.user")
        users = cursor.fetchall()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()

        assert((sql_environment['MYSQL_USER'],) in users)
        assert(("root",) in users)
        assert((sql_environment['MYSQL_DATABASE'],) in databases)

