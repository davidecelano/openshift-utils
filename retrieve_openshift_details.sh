#!/bin/bash

NAMESPACE=$1

if [ -z "$NAMESPACE" ]; then
  echo "Usage: $0 <namespace>"
  exit 1
fi

output_file="openshift_details.json"

echo "{" > $output_file

echo "\"deployments\": [" >> $output_file
echo "Retrieving deployment details..."
oc get deployments -n $NAMESPACE -o=jsonpath='{range .items[*]}{.metadata.name}{"\n"}{.spec.template.spec.containers[*].resources}{"\n"}{.status.replicas}{"\n"}{end}' >> $output_file
echo "]," >> $output_file

echo "\"deploymentconfigs\": [" >> $output_file
echo "Retrieving deploymentconfig details..."
oc get deploymentconfigs -n $NAMESPACE -o=jsonpath='{range .items[*]}{.metadata.name}{"\n"}{.spec.template.spec.containers[*].resources}{"\n"}{.status.replicas}{"\n"}{end}' >> $output_file
echo "]," >> $output_file

echo "\"statefulsets\": [" >> $output_file
echo "Retrieving statefulset details..."
oc get statefulsets -n $NAMESPACE -o=jsonpath='{range .items[*]}{.metadata.name}{"\n"}{.spec.template.spec.containers[*].resources}{"\n"}{.status.replicas}{"\n"}{end}' >> $output_file
echo "]," >> $output_file

echo "\"daemonsets\": [" >> $output_file
echo "Retrieving daemonset details..."
oc get daemonsets -n $NAMESPACE -o=jsonpath='{range .items[*]}{.metadata.name}{"\n"}{.spec.template.spec.containers[*].resources}{"\n"}{end}' >> $output_file
echo "]" >> $output_file

echo "}" >> $output_file
