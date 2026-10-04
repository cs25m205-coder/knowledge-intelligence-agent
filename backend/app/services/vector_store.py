import json
from pathlib import Path

import faiss
import numpy as np


class FAISSVectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatIP(dimension)
        self.chunk_ids = []

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        chunk_ids: list[int],
    ):
        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        self.index.add(embeddings)
        self.chunk_ids.extend(chunk_ids)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ):
        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            results.append(
                {
                    "chunk_id": self.chunk_ids[index],
                    "score": float(score),
                }
            )

        return results

    def save(
        self,
        index_path: str,
        metadata_path: str,
    ):
        index_path = Path(index_path)
        metadata_path = Path(metadata_path)

        index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(index_path),
        )

        metadata = {
            "chunk_ids": self.chunk_ids,
        }

        with open(
            metadata_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
            )

    @classmethod
    def load(
        cls,
        index_path: str,
        metadata_path: str,
    ):
        index = faiss.read_index(
            str(index_path)
        )

        with open(
            metadata_path,
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        store = cls(index.d)

        store.index = index
        store.chunk_ids = metadata["chunk_ids"]

        return store