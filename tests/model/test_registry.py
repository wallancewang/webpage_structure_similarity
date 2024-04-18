import unittest
from src.model.html_embedding import BowEmbedder, TextEmbedder, StructureEmbedder
from src.model.registry import EmbedRegistry


class EmbedRegistryTest(unittest.TestCase):
    def test_get_bow_model(self):
        model_cls = EmbedRegistry.get_embedding_cls('bow')
        self.assertEqual(model_cls, BowEmbedder)

    def test_get_text_model(self):
        model_cls = EmbedRegistry.get_embedding_cls('plain_text')
        self.assertEqual(model_cls, TextEmbedder)

    def test_get_structure_model(self):
        model_cls = EmbedRegistry.get_embedding_cls('html_structure')
        self.assertEqual(model_cls, StructureEmbedder)
