# DeployImageCaptioning

[Frontend lives here](http://37.27.222.64:8501/)


## Overview

<div style="display: flex; align-items: center;">

  <div style="flex: 1; padding: 10px;">
    <p>
      DeployImageCaptioning is the deployment of <a href="https://github.com/kalebsofer/ImageCaptioning" target="_blank">ImageCaptioning</a>, a multi-modal transformer for image captioning. The project is fully containerized, scalable, and modularised. It is deployed on a renter Hetzner server.
    </p>
    <p>
    The transformer architecture follows a similar design the <a href="https://arxiv.org/abs/1706.03762" target="_blank">Attention is All You Need</a> paper.
    </p>
  </div>

  <div style="flex: 1; padding: 10px;">
    <img src="public/images/transformer.png" alt="transformer" width="100%"/>
  </div>

</div>

## Container Architecture

The architecture is modular and scalable. Docker containers have a single purpose and are designed to be stateless.

- **Frontend**: Hosted using a Streamlit server, accessible at [http://65.109.142.90:8501/](http://65.109.142.90:8501/).
- **Backend**: Retrieves the model and performs inference on incoming audio transcription requests.
- **Storage**: MinIO is used to store different versions of the transcription model.
- **RDBS**: PostgreSQL is utilized to log user behavior and interactions.
- **Traffic**: Nginx is configured to handle traffic and SSL termination.
- **Reinforcement**: Spins up on a schedule, uses PostgreSQL logs for reinforcement, updates the model weights, and pushes the latest version to MinIO.

![Container Architecture](public/images/container_architecture.png)

## Stack



![Stack](public/images/stack.png)


## Local development
- update .env.prod in project root
- Build images
```bash
docker-compose --env-file .env.prod -f docker-compose.prod.yml build
```
- run containers
```bash
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d
```
- Merge to main for prod deploy

- To stop containers
```bash
docker-compose --env-file .env.prod -f docker-compose.prod.yml down
```

## Deployment Prerequisites

- **Remote Server**: Ensure you have a remote server set up.
- **Project Folder**: Create a project folder on your remote server.
- **Docker Installed**: Install Docker on your remote server.
- **Domain Name**: Associate your domain name with your remote server's IP address.
- **SSL Certificate**: Obtain an SSL certificate for your domain.

## Deployment Steps

1. **Update Domain References**:
   - Search and replace all instances of `inventiveimagecaption.com` in your repository with your actual domain name.

2. **Transfer Files to Remote**:
   - Use `scp` to copy `docker-compose.prod.yml` and `.env.prod` to your project folder on the remote server:
     ```bash
     scp docker-compose.prod.yml .env.prod user@your-remote-ip:/path/to/project-folder/
     ```

3. **Pull Docker Images**:
   - SSH into your remote server and navigate to your project folder. Then, pull the Docker images from Docker Hub:
     ```bash
     docker-compose -f docker-compose.prod.yml pull
     ```

4. **Run Containers**:
   - Start the containers using the `.env.prod` file and the `--no-build` flag:
     ```bash
     docker-compose --env-file .env.prod -f docker-compose.prod.yml up --no-build
     ```

