import json
import subprocess
import sys

def get_resource_details(resource_type, namespace):
    command = [
        "oc", "get", resource_type, "-n", namespace,
        "-o=jsonpath={range .items[*]}{.metadata.name}{\"\\n\"}{.spec.template.spec.containers[*].resources}{\"\\n\"}{.status.replicas}{\"\\n\"}{end}"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip().split("\n")

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
