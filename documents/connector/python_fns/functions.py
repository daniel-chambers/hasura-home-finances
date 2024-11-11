import os
from hasura_ndc import start
from hasura_ndc.instrumentation import with_active_span # If you aren't planning on adding additional tracing spans, you don't need this!
from opentelemetry.trace import get_tracer # If you aren't planning on adding additional tracing spans, you don't need this either!
from hasura_ndc.function_connector import FunctionConnector
from pydantic import BaseModel # You only need this import if you plan to have complex inputs/outputs, which function similar to how frameworks like FastAPI do
import asyncio # You might not need this import if you aren't doing asynchronous work
from hasura_ndc.errors import UnprocessableContent
from gmft.auto import CroppedTable, AutoTableDetector, AutoTableFormatter, TATRFormattedTable
from gmft_pymupdf import PyMuPDFDocument
from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions, AuthenticationRecord
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from msgraph.generated.drives.item.items.item.content.content_request_builder import ContentRequestBuilder
import urllib.parse

connector = FunctionConnector()
detector = AutoTableDetector()
formatter = AutoTableFormatter()

entra_tenant_id = os.getenv("MS_ENTRA_TENANT_ID")
entra_client_id = os.getenv("MS_ENTRA_CLIENT_ID")
entra_authentication_record = None if os.getenv("MS_ENTRA_AUTHENTICATION_RECORD") == None else AuthenticationRecord.deserialize(os.getenv("MS_ENTRA_AUTHENTICATION_RECORD"))

device_code_credential = DeviceCodeCredential(authentication_record=entra_authentication_record, cache_persistence_options=TokenCachePersistenceOptions(allow_unencrypted_storage=True), disable_automatic_authentication=True);
scopes = ["https://graph.microsoft.com/Files.Read.All", "https://graph.microsoft.com/User.Read"]
msgraph_client = GraphServiceClient(device_code_credential, scopes)

class PdfTable(BaseModel):
    markdown: str
    json: str

@connector.register_query
async def get_tables_from_pdf(file_id: str) -> list[PdfTable]:
    encoded_file_id = urllib.parse.quote(file_id, safe="")
    bytes = await ContentRequestBuilder(msgraph_client.request_adapter, msgraph_client.path_parameters).with_url(f"https://graph.microsoft.com/v1.0/me/drive/items/{encoded_file_id}/content").get()
    downloaded_file_path = "tempfile"
    with open(downloaded_file_path, "wb") as file:
        file.write(bytes)

    doc = PyMuPDFDocument(downloaded_file_path)
    cropped: list[CroppedTable] = []

    for page in doc:
        cropped += detector.extract(page)

    tables: list[TATRFormattedTable] = []
    for crop in cropped:
        tables.append(formatter.extract(crop))

    table_text: list[PdfTable] = []
    for table in tables:
        table_text.append(PdfTable(markdown=table.df().to_markdown(), json=table.df().to_json(orient="records")))

    doc.close()
    os.remove(downloaded_file_path)

    return table_text

class File(BaseModel):
    id: str
    name: str
    size: int
    type: str

@connector.register_query
async def get_files(path: str) -> list[File]:
    msgraph_client.drives.by_drive_id("").items.by_drive_item_id("").content
    params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(select=["id", "name", "size", "file", "folder"])
    request_config = ChildrenRequestBuilder.ChildrenRequestBuilderGetRequestConfiguration(query_parameters=params)
    encoded_path = urllib.parse.quote(path, safe="")
    drive_items = await ChildrenRequestBuilder(msgraph_client.request_adapter, msgraph_client.path_parameters).with_url(f"https://graph.microsoft.com/v1.0/me/drive/root:{encoded_path}:/children").get(request_config)

    files: list[File] = []
    for item in drive_items.value:
        files.append(File(id=item.id, name=item.name, size=item.size, type="file" if item.folder is None else "folder"))

    return files

if __name__ == "__main__":
    start(connector)
