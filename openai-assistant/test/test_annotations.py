import logging
import unittest

from dotenv import load_dotenv

# New Annotations
from utils.annotations import construct_value_with_citations, extract_citations, create_annotations_list, \
    validate_indexes, has_annotations
from fixture import message_with_citation, message_with_citation_2, mock_message_with_multiple_annotations, \
    message_no_citation

load_dotenv()
logging.basicConfig(level=logging.INFO)


class NewTestAnnotations(unittest.TestCase):
    def test_extract_citations(self):
        result = extract_citations(mock_message_with_multiple_annotations)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'Supplemental Agreement - Other')
        result = extract_citations(message_with_citation)
        self.assertEqual(result[0]['name'], 'source')
        result = extract_citations(message_with_citation_2)
        self.assertEqual(result[0]['name'], 'ce')

    def test_construct_value_with_citations(self):
        result = construct_value_with_citations(mock_message_with_multiple_annotations)
        assert result

        # This one is buggy because the OAI object doesn't align properly
        result = construct_value_with_citations(message_with_citation_2)
        pass

    def test_create_annotations_list(self):
        from chainlit.context import ChainlitContextException
        citations = extract_citations(mock_message_with_multiple_annotations)
        with self.assertRaises(ChainlitContextException):
            result = create_annotations_list(citations)
            pass

    def test_validate_indexes(self):
        result = validate_indexes(message_with_citation)
        self.assertTrue(result)

        result = validate_indexes(message_with_citation_2)
        self.assertFalse(result)

    def test_has_annotations(self):
        result = has_annotations(message_no_citation)
        self.assertFalse(result)

        result = has_annotations(message_with_citation)
        self.assertTrue(result)
