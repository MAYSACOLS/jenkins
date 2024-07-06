pipeline {
    environment {
        DOCKER_ID = "maysa56" // Remplacez par votre ID Docker Hub
        DOCKER_PASS = credentials("DOCKER_HUB_PWD") // On récupère le mot de passe Docker Hub à partir du secret texte appelé docker_hub_pass enregistré dans Jenkins
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

        stage('Test Acceptance') {
            parallel {
                stage('Test Cast Service') {
                    steps {
                        script {
                            sh 'curl localhost:8081' // Port spécifique pour cast-service
                        }
                    }
                }
                stage('Test Movie Service') {
                    steps {
                        script {
                            sh 'curl localhost:8082' // Port spécifique pour movie-service
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
                            runDockerImage("cast-service", 8081)
                        }
                    }
                }
                stage('Run Movie Service') {
                    steps {
                        script {
                            runDockerImage("movie-service", 8082)
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
   docker login -u maysa56 -p D@t@scientest_2024;
   # docker login -u $DOCKER_ID -p $DOCKER_PASS
    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
    """
}

def runDockerImage(MicroService, port) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    sh """
    docker rm -f ${MicroService} || true
    docker run -d -p ${port}:80 --name ${MicroService} $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
    sleep 10
    """
}

def deployToKubernetes(MicroService, environment) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    sh """
    cp exam/values.yaml values.yaml
    sed -i 's/tag:.*/tag: v.${env.BUILD_ID}.0/' values.yaml
    helm upgrade --install ${MicroService} ./${MicroService}/chart --values=values.yaml --namespace ${environment}
    """
}
