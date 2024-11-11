import os
from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions

entra_tenant_id = os.getenv("MS_ENTRA_TENANT_ID")
entra_client_id = os.getenv("MS_ENTRA_CLIENT_ID")
scopes = ["https://graph.microsoft.com/Files.Read.All", "https://graph.microsoft.com/User.Read"]

device_code_credential = DeviceCodeCredential(entra_client_id, tenant_id=entra_tenant_id, cache_persistence_options=TokenCachePersistenceOptions(allow_unencrypted_storage=True));
auth_record = device_code_credential.authenticate(scopes=scopes, enable_cae=True)
print("Authentication Record")
print(auth_record.serialize())
