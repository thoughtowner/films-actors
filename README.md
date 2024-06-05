# Launch Instructions:

### 1. Clone a project.
`git clone https://github.com/ilya-danilov/films-and-actors-hw`

### 2. Create an .env file.

```
PG_HOST=host.docker.internal
PG_PORT=<change_me>
PG_USER=<change_me>
PG_PASSWORD=<change_me>
PG_DBNAME=<change_me>

FLASK_PORT=5000

MYAPIFILMS_KEY=<your_token>
SECRET_KEY=<your_uuid>
```

### 3. Get a token for MYAPIFILMS_KEY on the website https://www.myapifilms.com/imdb.do and paste it into the .env file.

### 4. Generate any UUID and paste it into the .env file.

### 5. Launch a project.

Go to the project folder: `cd films-and-actors-hw`
Launch for the first time: `docker compose up --build`
In subsequent times: `docker compose up`
Stop the work: `docker compose stop`
Reset all project settings: `docker compose down`

### 6. Go to the website.
http://0.0.0.0:5000