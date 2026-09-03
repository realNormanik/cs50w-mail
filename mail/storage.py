import os
import uuid
import requests
from django.core.files.storage import Storage
from django.conf import settings


class VercelBlobStorage(Storage):
    BASE_URL = "https://blob.vercel-storage.com"

    def _headers(self, content_type="application/octet-stream"):
        return {
            "authorization": f"Bearer {settings.BLOB_READ_WRITE_TOKEN}",
            "x-api-version": "7",
            "content-type": content_type,
        }

    def _save(self, name, content):
        content_type = getattr(content, "content_type", "application/octet-stream")
        # unikamy kolizji nazw plików
        ext = os.path.splitext(name)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"

        response = requests.put(
            f"{self.BASE_URL}/{unique_name}",
            data=content.read(),
            headers=self._headers(content_type),
        )
        response.raise_for_status()
        self._last_url = response.json()["url"]
        return unique_name

    def _get_url_for(self, name):
        # Vercel Blob zwraca pełny URL przy uploadzie; tu odtwarzamy go
        # dla plików już istniejących (public store)
        return f"{self.BASE_URL.replace('blob.vercel-storage.com', settings.BLOB_STORE_ID + '.public.blob.vercel-storage.com')}/{name}"

    def url(self, name):
        return getattr(self, "_last_url", self._get_url_for(name))

    def exists(self, name):
        # Vercel Blob generuje unikalne nazwy, więc zwykle False wystarczy,
        # by uniknąć konfliktów; SDK i tak dorzuca losowy sufiks.
        return False

    def delete(self, name):
        requests.delete(
            f"{self.BASE_URL}/{name}",
            headers=self._headers(),
        )