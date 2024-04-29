import logging
import unittest

from dotenv import load_dotenv

from utils.annotations import OpenAIAdapter
from fixture import message_with_citation, \
    message_no_citation, message_with_invalid_index, message_with_multiple_annotations_no_quotes, \
    message_with_multiple_annotations, message_with_no_quote

load_dotenv()
logging.basicConfig(level=logging.INFO)


annotations_fixtures = [message_with_citation,  # 1
                        message_with_invalid_index,  # 0
                        message_no_citation,  # 0
                        message_with_multiple_annotations_no_quotes,  # 0
                        message_with_multiple_annotations,  # 3
                        message_with_no_quote  # 0
                        ]


class NewTestAnnotations(unittest.IsolatedAsyncioTestCase):

    async def test_all_fixtures(self):
        results = []
        expected_results = [1, 0, 0, 0, 3, 0]
        for message in annotations_fixtures:
            fixture = OpenAIAdapter(message)

            await fixture.main()

            self.assertTrue(fixture.get_content())
            pass

            results.append(len(fixture.elements))

        self.assertEqual(expected_results, results)

    async def test_citation_details(self):
        message = OpenAIAdapter(message_with_citation)
        await message.set_citations()
        message.validate_indexes()
        message.set_elements()
        self.assertTrue(message.elements)

    async def test_extract_citations(self):
        message = OpenAIAdapter(message_with_multiple_annotations_no_quotes)
        await message.set_citations()
        message.set_elements()
        result = message.elements
        self.assertEqual(len(result), 0)

        message = OpenAIAdapter(message_with_multiple_annotations)
        await message.set_citations()
        message.set_elements()
        result = message.elements
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], '[1] file-NHlneG03h2SdhS8Qzab5dbMw')
        self.assertEqual(result[1][0], '[2] file-NHlneG03h2SdhS8Qzab5dbMw')
        self.assertEqual(result[2][0], '[3] file-80O35GgEFpRE38EhT2HYe6qt')

    def test_construct_value_with_citations(self):

        for message in [message_with_multiple_annotations_no_quotes, message_with_invalid_index, message_with_no_quote]:
            result = OpenAIAdapter(message).get_content()
            self.assertTrue(result)

    async def test_create_annotations_list(self):
        message = OpenAIAdapter(message_with_multiple_annotations_no_quotes)
        await message.set_citations()
        message.set_elements()
        self.assertEqual(len(message.annotations), 3)

    def test_validate_indexes(self):
        result = OpenAIAdapter(message_with_citation).validate_indexes()
        self.assertTrue(result)

        result = OpenAIAdapter(message_with_invalid_index).validate_indexes()
        self.assertFalse(result)

    def test_has_annotations(self):
        result = OpenAIAdapter(message_no_citation).has_annotations()
        self.assertFalse(result)

        result = OpenAIAdapter(message_with_citation).has_annotations()
        self.assertTrue(result)

