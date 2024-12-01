pipeline {
    agent any

    stages {
        stage('Clonar Repositorio do Git e buildar os containers necessarios') {
            steps {
                script {
                    git branch: "main", url: "https://github.com/vinic1u/Trabalho_DevOps_2392132.git"
                    sh 'docker-compose down -v'
                    sh 'docker-compose build'
                }
            }
        }

        stage('Iniciar os containers e o Teste da aplicação') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test mysqld_exporter prometheus grafana'
                    sh 'sleep 40' 

                    try {
                        sh 'docker-compose run --rm test'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Testes da Aplicação Flask FALHARAM!!!. Pipipeline FINALIZADA"
                    }
                }
            }
        }

        stage('Manter a aplicação em execução') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test mysqld_exporter prometheus grafana'
                }
            }
        }
    }

    post {
        failure {
            sh 'docker-compose down -v'
        }
    }
}