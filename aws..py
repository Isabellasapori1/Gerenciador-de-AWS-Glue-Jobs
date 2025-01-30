import boto3

# Configurar as credenciais da AWS (é necessário configurar previamente no AWS CLI ou ~/.aws/credentials)
aws_region = "us-east-1"

# Criar cliente para cada serviço
ec2_client = boto3.client('ec2', region_name=aws_region)
s3_client = boto3.client('s3', region_name=aws_region)
rds_client = boto3.client('rds', region_name=aws_region)
lambda_client = boto3.client('lambda', region_name=aws_region)
iam_client = boto3.client('iam', region_name=aws_region)

# Nome do ambiente
env_name = "meu-ambiente-aws"

# Criar uma instância EC2
def criar_instancia_ec2():
    print("Criando instância EC2...")
    
    instance = ec2_client.run_instances(
        ImageId="ami-0c02fb55956c7d316",  # AMI padrão Amazon Linux 2
        InstanceType="t2.micro",
        KeyName="minha-chave-aws",  # Substituir pelo nome da sua chave SSH
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': env_name}]
        }]
    )

    instance_id = instance["Instances"][0]["InstanceId"]
    print(f"Instância EC2 criada com ID: {instance_id}")
    return instance_id

# Criar um bucket S3
def criar_bucket_s3():
    print("Criando bucket S3...")
    
    bucket_name = f"{env_name}-bucket"
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': aws_region}
    )
    
    print(f"Bucket S3 criado: {bucket_name}")
    return bucket_name

# Criar um banco de dados RDS
def criar_rds():
    print("Criando banco de dados RDS...")
    
    rds_client.create_db_instance(
        DBInstanceIdentifier=env_name,
        AllocatedStorage=20,
        DBInstanceClass="db.t3.micro",
        Engine="mysql",
        MasterUsername="admin",
        MasterUserPassword="MinhaSenhaForte123",  # Substituir por uma senha segura
        BackupRetentionPeriod=7,
        MultiAZ=False
    )
    
    print(f"Banco de dados RDS criado: {env_name}")

# Criar uma função Lambda
def criar_lambda():
    print("Criando função Lambda...")

    role_name = "LambdaExecutionRole"
    
    # Criar papel IAM para a função Lambda
    role = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": { "Service": "lambda.amazonaws.com" },
                    "Action": "sts:AssumeRole"
                }
            ]
        }"""
    )

    role_arn = role["Role"]["Arn"]
    print(f"Role IAM criada: {role_arn}")

    # Criar a função Lambda
    response = lambda_client.create_function(
        FunctionName=f"{env_name}-lambda",
        Runtime="python3.9",
        Role=role_arn,
        Handler="lambda_function.lambda_handler",
        Code={
            "ZipFile": b"def lambda_handler(event, context):\n    return {'statusCode': 200, 'body': 'Hello from Lambda!'}"
        },
        Timeout=10,
        MemorySize=128
    )

    print(f"Função Lambda criada: {response['FunctionArn']}")
    return response['FunctionArn']

# Criar os recursos AWS
def criar_ambiente():
    print("🔹 Iniciando criação do ambiente AWS...")
    
    instancia_id = criar_instancia_ec2()
    bucket = criar_bucket_s3()
    criar_rds()
    lambda_arn = criar_lambda()

    print("\n✅ Ambiente criado com sucesso!")
    print(f"EC2 ID: {instancia_id}")
    print(f"Bucket S3: {bucket}")
    print(f"Lambda ARN: {lambda_arn}")

if __name__ == "__main__":
    criar_ambiente()
