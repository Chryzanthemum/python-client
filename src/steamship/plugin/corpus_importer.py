from abc import ABC
from typing import Any

from steamship.base import Client
from steamship.client.operations.corpus_importer import (
    CorpusImportRequest,
    CorpusImportResponse,
)
from steamship.plugin.service import PluginRequest, PluginService


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Corpus Importer.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.corpus_importer instead
# of this file.
#
class CorpusImporter(PluginService[CorpusImportRequest, CorpusImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(
        cls, d: Any, client: Client = None
    ) -> PluginRequest[CorpusImportRequest]:
        return CorpusImportRequest.from_dict(d, client=client)