import json
import subprocess
import sys
import csv

def get_resource_details(resource_type, namespace):
    command = [
        "oc", "get", resource_type, "-n", namespace,
        "-o=jsonpath={range .items[*]}{.metadata.name}{\"\\n\"}{.metadata.namespace}{\"\\n\"}{.kind}{\"\\n\"}{.spec.template.spec.containers[*].resources}{\"\\n\"}{.spec.template.spec.containers[*].readinessProbe.initialDelaySeconds}{\"\\n\"}{.status.replicas}{\"\\n\"}{.spec.replicas}{\"\\n\"}{.spec.replicas}{\"\\n\"}{end}"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    details = result.stdout.strip().split("\n")
    
    resources = []
    for i in range(0, len(details), 8):
        if len(details) - i < 8:
            continue
        resource = {
            "name": details[i] if i < len(details) else "NotSet",
            "namespace": details[i+1] if i+1 < len(details) else "NotSet",
            "type": details[i+2] if i+2 < len(details) else "NotSet",
            "limits": details[i+3] if i+3 < len(details) else "NotSet",
            "requests": details[i+3] if i+3 < len(details) else "NotSet",
            "readiness_probe_time": details[i+4] if i+4 < len(details) else "NotSet",
            "current_replicas": details[i+5] if i+5 < len(details) else "NotSet",
            "min_replicas": details[i+6] if i+6 < len(details) else "NotSet",
            "max_replicas": details[i+7] if i+7 < len(details) else "NotSet"
        }
        resources.append(resource)
    
    return resources

def write_csv(details, output_file):
    with open(output_file, "w", newline='') as csvfile:
        fieldnames = ["name", "namespace", "type", "limits", "requests", "readiness_probe_time", "current_replicas", "min_replicas", "max_replicas"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        for resource_type, resources in details.items():
            for resource in resources:
                writer.writerow(resource)

def main():
    if len(sys.argv) != 4:
        print("Usage: python retrieve_openshift_details.py <namespace> <output_file> <output_format>")
        sys.exit(1)

    namespace = sys.argv[1]
    output_file = sys.argv[2]
    output_format = sys.argv[3].lower()

    details = {
        "deployments": get_resource_details("deployments", namespace),
        "deploymentconfigs": get_resource_details("deploymentconfigs", namespace),
        "statefulsets": get_resource_details("statefulsets", namespace),
        "daemonsets": get_resource_details("daemonsets", namespace)
    }

    if output_format == "json":
        with open(output_file, "w") as f:
            json.dump(details, f, indent=4)
    elif output_format == "csv":
        write_csv(details, output_file)
    else:
        print("Invalid output format. Please choose 'json' or 'csv'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
