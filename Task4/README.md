# CI/CD Pipeline for Python E-Commerce Application

## Overview
This project defines a CI/CD pipeline using GitLab CI/CD to automate building, testing, scanning, and deploying a Python-based E-Commerce application. The pipeline consists of multiple stages, including preparing dependencies, running tests, scanning for vulnerabilities, deploying files to a staging server, and building and pushing a Docker image.

---

## Prerequisites
Before running the pipeline, ensure the following are set up:

### **1. EC2 Staging Server Setup**
- Launch an **Ubuntu EC2 instance** on AWS to act as the staging server.
- Allow SSH access by opening **port 22** in the **Security Group**.

### **2. Set Up CI/CD Variables** (in GitLab Settings > CI/CD > Variables)
- DOCKER_USERNAME: Your Docker Hub username.
- DOCKERHUB_TOKEN: Your Docker Hub access token.
- EC2_HOST: The public IP or hostname of the EC2 instance.
- EC2_USER: The user on the EC2 server
- EC2_SSH_PRIVATE_KEY: The private SSH key for connecting to the EC2 instance.

---

## Pipeline Stages

### **Prepare Stage**
Installs dependencies and sets up the application:
```yaml
prepare:
  stage: prepare
  script:
    - pip install --upgrade pip
    - pip install -r requirements.txt
    - python manage.py collectstatic --noinput
    - python manage.py migrate
    - mkdir -p $BUILD_DIR
    - cp -r static_root/ $BUILD_DIR/static
    - cp -r demo/ $BUILD_DIR/code
  artifacts:
    paths:
      - $BUILD_DIR
```

### **Test Stage**
Runs **pytest** to ensure application functionality:
```yaml
test:
  stage: test
  script:
    - pip install pytest
    - pytest || echo "No Tests Found..."
#   allow_failure: true
```

### **Code Scan Stage**
Uses **Bandit** to scan for Python security issues:
```yaml
code-scan:
  stage: code-scan
  script:
    - pip install bandit
    - bandit -r .
#   allow_failure: true
```

### **Deploy Files to EC2 Server**
Transfers built artifacts to the staging server:
```yaml
deploy-files:
  stage: deploy-files
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - mkdir -p ~/.ssh
    - echo "$EC2_SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan -H $EC2_HOST >> ~/.ssh/known_hosts
    - scp -r $BUILD_DIR/* $EC2_USER@$EC2_HOST:/home/$EC2_USER
  needs: ["prepare", "test", "code-scan"]
```

### **Build Docker Image**
Creates a Docker image from the application:
```yaml
build_docker_image:
  stage: docker-build
  image: docker:latest
  services:
    - docker:24.0.5-dind
  script:
    - docker build -t $DOCKER_IMAGE:$DOCKER_TAG -t $DOCKER_IMAGE:latest .
    - docker save -o image.tar $DOCKER_IMAGE:$DOCKER_TAG $DOCKER_IMAGE:latest
  artifacts:
    paths:
      - image.tar
  needs: ["code-scan", "prepare", "test"]
```

### **Scan Docker Image for Vulnerabilities**
Uses **Trivy** to check for security vulnerabilities:
```yaml
docker-scan:
  stage: docker-scan
  image:
    name: docker.io/aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --input image.tar --exit-code 1 --severity HIGH,CRITICAL
  allow_failure: true
  needs: ["build_docker_image"]
```

### **Push Docker Image to Docker Hub**
Uploads the built image to Docker Hub:
```yaml
docker-push:
  stage: docker-push
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - echo "$DOCKERHUB_TOKEN" | docker login --username "$DOCKER_USERNAME" --password-stdin
  script:
    - docker load -i image.tar
    - docker push $DOCKER_IMAGE:$DOCKER_TAG
  needs: ["docker-scan", "build_docker_image"]
```  