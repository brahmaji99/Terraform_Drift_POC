pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['dev', 'stage', 'prod'], description: 'Environment')
        booleanParam(name: 'APPLY', defaultValue: false, description: 'Apply changes?')
    }

    environment {
        AWS_DEFAULT_REGION = 'ap-southeast-2'
    }

    stages {

        stage('Checkout') {
            steps {
                // Checkout the 'main' branch of the public GitHub repo
                git branch: 'main', url: 'https://github.com/brahmaji99/Terraform_Drift_POC.git'
            }
        }

        stage('Init') {
            steps {
                dir("environments/${params.ENV}") {
                    sh 'terraform init'
                }
            }
        }

        stage('Validate') {
            steps {
                dir("environments/${params.ENV}") {
                    sh 'terraform validate'
                }
            }
        }

        stage('Format Check') {
            steps {
                dir("environments/${params.ENV}") {
                    sh 'terraform fmt'
                }
            }
        }

        stage('Plan') {
            steps {
                dir("environments/${params.ENV}") {
                    script {
                        // Run terraform plan and capture exit code
                        def exitCode = sh(
                            script: 'terraform plan -detailed-exitcode -out=tfplan; echo $?',
                            returnStdout: true
                        ).trim()

                        echo "Terraform exit code: ${exitCode}"

                        // Save to file for Drift Detection stage
                        writeFile file: 'exitcode', text: exitCode
                    }
                }
            }
        }

        stage('Drift Detection') {
            steps {
                dir("environments/${params.ENV}") {
                    script {
                        def exitCode = readFile('exitcode').trim()

                        if (exitCode == "2") {
                            echo "Drift detected!"
                        } else if (exitCode == "0") {
                            echo "No changes"
                        } else {
                            error "Terraform plan failed"
                        }
                    }
                }
            }
        }
        stage('Manual Approval') {
            when {
                expression { params.APPLY == true }
            }
            steps {
                input message: "Approve apply for ${params.ENV}?"
            }
        }

        stage('Apply') {
            when {
                expression { params.APPLY == true }
            }
            steps {
                dir("environments/${params.ENV}") {
                    sh 'terraform apply -auto-approve tfplan'
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}