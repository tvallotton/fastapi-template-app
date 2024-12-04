#!/bin/bash


# Instala AWS CLI
pip install awscli

# Define los nombres de los buckets que quieres crear
buckets=("test")

# Define la configuración de CORS
cors_configuration='{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}'

aws configure set aws_access_key_id '-'
aws configure set aws_secret_access_key '-'
# Crea los buckets y configura CORS
for bucket in "${buckets[@]}"; do
  echo $bucket
  aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket $bucket
  aws --endpoint-url=http://localhost:4566 s3api put-bucket-cors --bucket $bucket --cors-configuration "$cors_configuration"
done


  