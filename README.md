# Launch Instructions:

### 1. Clone a project.
`git clone https://github.com/thoughtowner/films-actors`

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

### 3. Get a token on the website https://www.myapifilms.com/imdb.do and paste it for MYAPIFILMS_KEY into the .env file.

### 4. Generate any UUID and paste it for SECRET_KEY into the .env file.

### 5. Launch a project.

Go to the project folder: `cd films-actors`
Launch for the first time: `docker compose up --build`
In subsequent times: `docker compose up`
Stop the work: `docker compose stop`
Reset all project settings: `docker compose down`

### 6. Go to the path.
http://0.0.0.0:5000
