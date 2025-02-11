import json
import subprocess
import sys
import csv

def convert_cpu_to_millicores(cpu_value):
    if cpu_value == "":
        return "NotSet"
    if cpu_value.endswith("m"):
        return int(cpu_value[:-1])
    return int(float(cpu_value) * 1000)

def convert_memory_to_mib(memory_value):
    if memory_value == "":
        return "NotSet"
    if memory_value.endswith("Mi"):
        return int(memory_value[:-2])
    elif memory_value.endswith("Gi"):
        return int(float(memory_value[:-2]) * 1024)
    elif memory_value.endswith("Ki"):
        return int(float(memory_value[:-2]) / 1024)
    return int(memory_value)

def get_resource_details(resource_type, namespace):
    command = [
        "oc", "get", resource_type, "-n", namespace,
        "-o=jsonpath={range .items[*]}{.metadata.name}{\"\\n\"}{.metadata.namespace}{\"\\n\"}{.kind}{\"\\n\"}{.spec.template.spec.containers[*].resources.limits.cpu}{\"\\n\"}{.spec.template.spec.containers[*].resources.limits.memory}{\"\\n\"}{.spec.template.spec.containers[*].resources.requests.cpu}{\"\\n\"}{.spec.template.spec.containers[*].resources.requests.memory}{\"\\n\"}{.spec.template.spec.containers[*].readinessProbe.initialDelaySeconds}{\"\\n\"}{.status.replicas}{\"\\n\"}{.spec.replicas}{\"\\n\"}{.spec.replicas}{\"\\n\"}{end}"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    details = result.stdout.strip().split("\n")
    
    resources = []
    for i in range(0, len(details), 11):
        if len(details) - i < 11:
            continue
        resource = {
            "name": details[i] if i < len(details) else "NotSet",
            "namespace": details[i+1] if i+1 < len(details) else "NotSet",
            "type": details[i+2] if i+2 < len(details) else "NotSet",
            "limits.cpu": convert_cpu_to_millicores(details[i+3]) if i+3 < len(details) else "NotSet",
            "limits.memory": convert_memory_to_mib(details[i+4]) if details[i+4] != "" else "NotSet",
            "requests.cpu": convert_cpu_to_millicores(details[i+5]) if i+5 < len(details) else "NotSet",
            "requests.memory": convert_memory_to_mib(details[i+6]) if details[i+6] != "" else "NotSet",
            "readiness_probe_time": details[i+7] if i+7 < len(details) else "NotSet",
            "current_replicas": details[i+8] if i+8 < len(details) else "NotSet",
            "min_replicas": details[i+9] if i+9 < len(details) else "NotSet",
            "max_replicas": details[i+10] if i+10 < len(details) else "NotSet"
        }
        resources.append(resource)
    
    return resources

def write_csv(details, output_file):
    with open(output_file, "w", newline='') as csvfile:
        fieldnames = ["name", "namespace", "type", "limits.cpu", "limits.memory", "requests.cpu", "requests.memory", "readiness_probe_time", "current_replicas", "min_replicas", "max_replicas"]
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
