# Recommendation API

This project implements a recommendation system using the Implicit Alternating Least Squares (ALS) model. The system provides personalized recommendations based on user interactions and serves the recommendations via a FastAPI-based API.

## Features

- Personalized recommendations based on user events
- API endpoint to receive recommendations
- Dockerized for easy deployment
- Swagger documentation for API endpoints

### Prerequisites

- Docker
- Python 3.11

### Usage

1. Clone the repository:

```bash
git clone https://github.com/yourusername/recommendation-api.git
cd recommendation-api
```

2. Build docker image

```bash
docker build -t recommendation-api .
```

3. Run the container

```bash
docker run -d -p 80:80 recommendation-api
```

### Access API Info

http://localhost:80/docs -> to view the Swagger documentation and test the API.

Example user ID for API test: 0001d86ea81e6eef12cebaa1dcbdadc2
