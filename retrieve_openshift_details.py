import json
import subprocess
import sys

def get_resource_details(resource_type, namespace):
    command = [
        "oc", "get", resource_type, "-n", namespace,
        "-o=jsonpath={range .items[*]}{.metadata.name}{\"\\n\"}{.metadata.namespace}{\"\\n\"}{.kind}{\"\\n\"}{.spec.template.spec.containers[*].resources}{\"\\n\"}{.spec.template.spec.containers[*].readinessProbe.initialDelaySeconds}{\"\\n\"}{.status.replicas}{\"\\n\"}{.spec.replicas}{\"\\n\"}{.spec.replicas}{\"\\n\"}{end}"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    details = result.stdout.strip().split("\n")
    
    resources = []
    for i in range(0, len(details), 8):
        resource = {
            "name": details[i],
            "namespace": details[i+1],
            "type": details[i+2],
            "limits": details[i+3],
            "requests": details[i+3],
            "readiness_probe_time": details[i+4] if details[i+4] else "NotSet",
            "current_replicas": details[i+5],
            "min_replicas": details[i+6] if details[i+6] else "NotSet",
            "max_replicas": details[i+7] if details[i+7] else "NotSet"
        }
        resources.append(resource)
    
    return resources

def main():
    if len(sys.argv) != 3:
        print("Usage: python retrieve_openshift_details.py <namespace> <output_file>")
        sys.exit(1)

    namespace = sys.argv[1]
    output_file = sys.argv[2]

    details = {
        "deployments": get_resource_details("deployments", namespace),
        "deploymentconfigs": get_resource_details("deploymentconfigs", namespace),
        "statefulsets": get_resource_details("statefulsets", namespace),
        "daemonsets": get_resource_details("daemonsets", namespace)
    }

    with open(output_file, "w") as f:
        json.dump(details, f, indent=4)

if __name__ == "__main__":
    main()
