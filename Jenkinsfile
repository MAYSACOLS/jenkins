pipeline {
    environment {
        DOCKER_ID = "maysa56" // Remplacez par votre ID Docker Hub
        DOCKER_PWD = credentials("DOCKER_HUB_PWD") // Récupération du mot de passe Docker Hub
        KUBECONFIG = credentials("config")
        HELM_RELEASE_NAME = 'app'
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

        stage('Run Docker Images') {
            parallel {
                stage('Run Cast Service') {
                    steps {
                        script {
                            buildAndRunDockerImage("cast-service", 8081)
                        }
                    }
                }
                stage('Run Movie Service') {
                    steps {
                        script {
                            buildAndRunDockerImage("movie-service", 8082)
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
                            echo 'Testing Cast Service'
                        }
                    }
                }
                stage('Test Movie Service') {
                    steps {
                        script {
                            echo 'Testing Movie Service'
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

        stage('Deploy to Kubernetes') {
            parallel {
                stage('Deploy Dev Cast Service') {
                    steps {
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('cast-service', 'dev')
                            }
                        }
                    }
                }
                stage('Deploy Dev Movie Service') {
                    steps {
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('movie-service', 'dev')
                            }
                        }
                    }
                }

                stage('Deploy QA Cast Service') {
                    steps {
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('cast-service', 'qa')
                            }
                        }
                    }
                }
                stage('Deploy QA Movie Service') {
                    steps {
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('movie-service', 'qa')
                            }
                        }
                    }
                }

                stage('Deploy Staging Cast Service') {
                    steps {
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('cast-service', 'staging')
                            }
                        }
                    }
                }
                stage('Deploy Staging Movie Service') {
                    steps {
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('movie-service', 'staging')
                            }
                        }
                    }
                }

                stage('Deploy Prod Cast Service') {
                    steps {
                        timeout(time: 15, unit: "MINUTES") {
                            input message: 'Do you want to deploy to prod?', ok: 'Yes'
                        }
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('cast-service', 'prod')
                            }
                        }
                    }
                }
                stage('Deploy Prod Movie Service') {
                    steps {
                        timeout(time: 15, unit: "MINUTES") {
                            input message: 'Do you want to deploy to prod?', ok: 'Yes'
                        }
                        script {
                            withEnv(["KUBECONFIG=${KUBECONFIG}"]) {
                                deployToKubernetes('movie-service', 'prod')
                            }
                        }
                    }
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

def deployToKubernetes(MicroService, environment) {
    def DOCKER_IMAGE = "examjenkinsdst"
    def DOCKER_TAG = "${MicroService}-v.${env.BUILD_ID}.0"

    // Copy kubeconfig file securely
    sh """
    mkdir -p $HOME/.kube
    cp ${KUBECONFIG} $HOME/.kube/config
    """

    // Copy Helm values file and update image tag
    sh """
    cp fastapi/values.yaml values.yml
    sed -i 's+tag.*+tag: ${DOCKER_TAG}+g' values.yml
    """

    // Check if Helm release already exists
    def releaseExists = sh(script: "helm list -q ${HELM_RELEASE_NAME} --namespace ${environment} | wc -l", returnStatus: true).trim()

    if (releaseExists == 0) {
        // Install Helm chart if release does not exist
        sh "helm install ${HELM_RELEASE_NAME} ./fastapi --values=values.yml --namespace ${environment}"
    } else {
        // Upgrade Helm chart if release exists
        sh "helm upgrade ${HELM_RELEASE_NAME} ./fastapi --values=values.yml --namespace ${environment}"
    }
}
