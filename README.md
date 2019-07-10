# sc_r_mailmarketing

## Architecture

Whole application is divided into two services:
 - **web** - which allows to manage contacts, segments, email templates and campaigns, and
 provided UI interface to the user
 - **email_client** - which stores details needed for the email gateway and contacts the
 email gateway directly.
 
Such division was chosen mainly due to two following reasons:
 - separation of responsibilities and concerns, recognizing one area of managing the
 resources, and the second of managing email sending
 - as architectural division between user-facing, exposed application, and the backend
 service keeping additionally sensitive data (gateway credentials).
 
Both services are developed using asyncio with tornado. For storage, the provided
implementations are aiopg for PostgresSQL as data storage for web service, and Redis
as sample data storage for the email_client (as stored data is relatively simple, any
key-value storage or cloud dedicated storage would be sufficient). Services contact
each other over HTTP interfaces.

## Setup

Create virtual environment, activate it and install the dependencies:

```
pip install -r requirements.txt
```

Additional packages may be required for proper installation of the postgres and redis
libraries. Note: as both app and tests can be ran using only docker images, this step
can be entirely skipped.

## Running application

There are three docker-compose files provided, each with different setup of the
application system.

### docker-compose.mock.yml

Contains both app services, redis, postgres db and mock third-party email service.
Allows local testing of the application, without the external dependencies. For testing
purposes, statuses returned by the mock are randomized. Run this configuration using:

```
docker-compose -f docker-compose.mock.yml up
```

And access the application via browser on `http://localhost:5050/`

### docker-compose.test.yml

Contains both app services, redis and postgres db. Allows local testing, already using
the external service dependency.

```
docker-compose -f docker-compose.test.yml up
```

And access the application via browser on `http://localhost:5050/`. Keep in mind that
all email requests will be failing until you setup the authentication credentials in
the settings tab.

### docker-compose.yml

For potential used in deployment, with external storage services and app source inside
the image instead of shared using volume. Not currently configured.

## Running tests

To run unit tests run `pytest` in project directory. As DB repositories were used to 
test the correctness of the queries as well, they are depending on the database
connection. If no database is available or configured, those tests will be skipped.

To configure the database PostgreSQL connection, modify the `config/database-test.json`
file. Alternatively, run all tests in containers:

**Setup**

```bash
docker build -t scr-python -f Dockerfile.local .
docker network create --driver bridge test_network
docker run -d -e POSTGRES_PASSWORD='surge' \
 -e POSTGRES_DB='testdb' \
 -e POSTGRES_USER='surge' \
 -p 5432:5432 \
 --name testpostgres \
 --network=test_network \
 postgres:9.6.14-alpine
```

**Running tests:**

```bash
docker run -v "$(pwd)":/app --network=test_network --name testrunner scr-python pytest && docker rm testrunner
```

## Known issues

1. Architectural / design
    - Email client does not persist the status of its tasks (email jobs) - 
    in case of web being down or email client failure, the status update or job itself
    might be lost.
    - Database initialization / migration mechanism is heavily simplified.
2. Feature
    - Lack of user induced retry of jobs from email campaign (after the system retries 
    are depleted).
3. Security simplifications
    - No authentication system for user, or system - the job update can be easily
    spoofed.
    - CSRF protection not enabled.
    - Gateway credentials are not encrypted in the email_client service.
4. UI / UX
    - Skipped pagination for templates, campaigns and on the details pages for related
    objects.
    - User is not informed in any way that `From` email or email gateway credentials are
    not set.