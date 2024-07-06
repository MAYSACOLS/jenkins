pipeline {
    environment {
        DOCKER_ID = "maysa56" // Remplacez par votre ID Docker Hub
        DOCKER_PWD = credentials("DOCKER_HUB_PWD") // Récupération du mot de passe Docker Hub
        KUBECONFIG = credentials("config")
    }
    agent any

    stages {
        stage('Build Docker Images') {
            parallel {
                stage('Build Cast Service') {
                    steps {
                        script {
                            buildDockerImage("cast-service")
                        }
                    }
                }
                stage('Build Movie Service') {
                    steps {
                        script {
                            buildDockerImage("movie-service")
                        }
                    }
                }
            }
        }

        stage('Push Docker Images') {
            parallel {
                stage('Push Cast Service') {
                    steps {
                        script {
                            pushDockerImage("cast-service")
                        }
                    }
                }
                stage('Push Movie Service') {
                    steps {
                        script {
                            pushDockerImage("movie-service")
                        }
                    }
                }
            }
        }

        stage('Run Docker Images') {
            parallel {
                stage('Run Cast Service') {
                    steps {
                        script {
                            def serviceName = "cast-service"
                            def port = 8081
                            buildAndRunDockerImage(serviceName, port)
                        }
                    }
                }
                stage('Run Movie Service') {
                    steps {
                        script {
                            def serviceName = "movie-service"
                            def port = 8082
                            buildAndRunDockerImage(serviceName, port)
                        }
                    }
                }
            }
        }

        stage('Test Acceptance') {
            parallel {
                stage('Test Cast Service') {
                    steps {
                        script {
                            testDockerImage(8081)
                        }
                    }
                }
                stage('Test Movie Service') {
                    steps {
                        script {
                            testDockerImage(8082)
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Setup kubeconfig
                    sh 'mkdir -p $HOME/.kube'
                    sh 'cp $KUBECONFIG $HOME/.kube/config'

                    // Deploy Cast Service
                    deployToKubernetes('cast-service', 'DEV')
                    deployToKubernetes('cast-service', 'QA')
                    deployToKubernetes('cast-service', 'STAGING')
                    deployToKubernetes('cast-service', 'PROD')

                    // Deploy Movie Service
                    deployToKubernetes('movie-service', 'DEV')
                    deployToKubernetes('movie-service', 'QA')
                    deployToKubernetes('movie-service', 'STAGING')
                    deployToKubernetes('movie-service', 'PROD')
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}

def buildDockerImage(MicroService) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    sh """
    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG ./$MicroService
    """
}

def pushDockerImage(MicroService) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    sh """
    echo "$DOCKER_PWD" | docker login -u "$DOCKER_ID" --password-stdin
    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
    """
}

def buildAndRunDockerImage(MicroService, port) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    sh """
    docker rm -f ${MicroService} || true
    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG ./$MicroService
    docker run -d -p ${port}:80 --name ${MicroService} $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
    sleep 10
    """
}

def testDockerImage(port) {
    sh """
    sleep 10
    curl -f http://localhost:${port}
    """
}

def deployToKubernetes(MicroService, environment) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    sh """
    rm -Rf .kube
    mkdir .kube
    ls
    cat $KUBECONFIG > .kube/config
    cp fastapi/values.yaml values.yml
    cat values.yml
    sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values.yml
    helm upgrade --install app fastapi --values=values.yml --namespace ${environment}
      """
}
