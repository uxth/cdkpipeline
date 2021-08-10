#!/bin/bash
for i in $(echo $(aws iam list-access-keys --user-name map-eks-cluster-admin) | jq -r '.AccessKeyMetadata[] | .AccessKeyId'); do aws iam delete-access-key --user-name map-eks-cluster-admin --access-key-id $i; done

echo $(aws iam create-access-key --user-name map-eks-cluster-admin) > key.json
KEY=$(aws secretsmanager get-secret-value --secret-id eks_admin_secrets)
if [ $? -ne 0 ]
  then
  aws secretsmanager create-secret --name eks_admin_secrets --secret-string file://key.json
fi
aws secretsmanager update-secret --secret-id eks_admin_secrets --secret-string file://key.json
rm -f key.json