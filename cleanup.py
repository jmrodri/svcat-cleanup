from kubernetes import client, config
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import NotFoundError
import sys

k8s_client = config.new_client_from_config()
dyn_client = DynamicClient(k8s_client)

service_bindings = dyn_client.resources.get(api_version='servicecatalog.k8s.io/v1beta1', kind='ServiceBinding')
secrets = dyn_client.resources.get(api_version='v1', kind='Secret')
bindings = service_bindings.get()
for binding in bindings.items:
    print(binding.metadata.name)
    print(binding.spec.secretName)
    try:
        da_secret = secrets.get(name=binding.spec.secretName, namespace=binding.metadata.namespace)
        print("\n")
        print("name ", da_secret.metadata.name)
        print(type(da_secret.metadata.ownerReferences))
        print(dir(da_secret.metadata.ownerReferences))
        for owner in da_secret.metadata.ownerReferences:
            # <class 'openshift.dynamic.client.ResourceField'>
            print(dir(owner))
            if owner.apiVersion == "servicecsatalog.k8s.io/v1beta1":
                # we can delete this reference

    except NotFoundError:
        print("Secret %s not found, skipping" % binding.spec.secretName)
    except TypeError:
        print("Invalid type")
    except:
        print("Unexected error:", sys.exc_info()[0])

