#!/usr/bin/python

from kubernetes import config
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import NotFoundError
import sys
import traceback

k8s_client = config.new_client_from_config()
dyn_client = DynamicClient(k8s_client)

service_bindings = dyn_client.resources.get(api_version='servicecatalog.k8s.io/v1beta1', kind='ServiceBinding')
secrets = dyn_client.resources.get(api_version='v1', kind='Secret')
bindings = service_bindings.get()
print("Found %d service binding(s)." % len(bindings.items))
for binding in bindings.items:
    print("Processing secret [%s] from service binding [%s] " %
          (binding.spec.secretName, binding.metadata.name))

    try:
        da_secret = secrets.get(name=binding.spec.secretName, namespace=binding.metadata.namespace)
        print("name: %s" % da_secret.metadata.name)

        if da_secret.metadata.ownerReferences is not None:
            print(type(da_secret.metadata.ownerReferences))
            # print(dir(da_secret.metadata.ownerReferences))
            print(len(da_secret.metadata.ownerReferences))
        else:
            print("No owner references found")
            break

        for index, owner in enumerate(da_secret.metadata.ownerReferences):
            # for owner in da_secret.metadata.ownerReferences:
            # <class 'openshift.dynamic.client.ResourceField'>
            if owner.apiVersion == "servicecatalog.k8s.io/v1beta1":
                # we can delete this reference
                print("Deleting the servicecatalog owner reference from secret %s" % da_secret.metadata.name)
                da_secret.metadata.ownerReferences.pop(index)
                print(da_secret.metadata.ownerReferences)
        secrets.patch(body=da_secret, namespace=binding.metadata.namespace, content_type='application/merge-patch+json')
    except NotFoundError:
        print("Secret %s not found, skipping" % binding.spec.secretName)
    except TypeError:
        print("Invalid type")
        traceback.print_exc()
    except:
        print("Unexected error: %s" % sys.exc_info()[0])
        traceback.print_exc()
