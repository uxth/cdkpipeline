#!/bin/bash
ENV=$1
if [[ $ENV == '' ]]
  then
  ENV=test
fi
key=$(echo -E $(aws secretsmanager get-secret-value --secret-id eks_admin_secrets) | jq -r '.SecretString')
aws configure set profile.$ENV-eks-admin.aws_access_key_id $(echo $key | jq -r '.AccessKey.AccessKeyId')
aws configure set profile.$ENV-eks-admin.aws_secret_access_key $(echo $key | jq -r '.AccessKey.SecretAccessKey')
if [[ $ENV == 'test' ]]; then
  aws eks update-kubeconfig --region us-west-2 --name map-eks-cluster --role-arn arn:aws:iam::711208530951:role/map-eks-cluster-role --profile $ENV-eks-admin --alias $ENV
elif [[ $ENV == 'dev' ]]; then
  aws eks update-kubeconfig --region us-west-2 --name map-eks-cluster --role-arn arn:aws:iam::182732313984:role/map-eks-cluster-role --profile $ENV-eks-admin --alias $ENV
fi
