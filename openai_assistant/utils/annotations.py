"""
Map OpenAI's ThreadMessage to Chainlit's Message objects.

We check for file annotation, and do some modification to the content to format reference notes.

We've had a lot of bugs with OpenAI's annotations, so we have to validate the indexes to make sure we don't do substitutions on the wrong indexes, or have missing annotations.

"""

from chainlit import Message
from chainlit.logger import logger
from openai.types import FileObject
from openai.types.beta.threads import (
    Message as ThreadMessage
)
from openai.types.beta.threads.file_citation_annotation import FileCitation as TextAnnotationFileCitationFileCitation, \
    FileCitationAnnotation as TextAnnotationFileCitation

from utils.openai_utils import initialize_openai_client


class OpenAIAdapter:
    """
    This class is responsible for adapting OpenAI's ThreadMessage to Chainlit's Message object.
    """

    def __init__(self, message: ThreadMessage) -> None:
        self.client = initialize_openai_client()
        self._id: str = message.id
        self.message: ThreadMessage = message
        # We're putting these in reverse order so we can work backward in get_content
        self.annotations: list[TextAnnotationFileCitation] = sorted(
            self.message.content[0].text.annotations,
            key=lambda x: x.start_index,
            reverse=True,
        )
        self.citations: list[TextAnnotationFileCitationFileCitation] = []
        self.elements: list[(str, str)] = []
        self.files_cache: dict = {}

    def has_annotations(self) -> bool:
        return bool(self.annotations)

    def validate_indexes(self) -> bool:
        """
        We've seen issues with OAI misaligning the indexes of the annotations. We use this to make sure we don't do substitutions on the wrong indexes.
        """
        content: str = self.message.content[0].text.value

        for annotation in self.annotations:
            citation = content[annotation.start_index: annotation.end_index].strip()
            if citation[0] != "【" or citation[-1] != "】":
                return False
        return True

    async def set_citations(self) -> None:
        for annotation in self.annotations:
            citation = annotation.file_citation
            try:
                if citation.file_id in self.files_cache:
                    retrieved_file: FileObject = self.files_cache[citation.file_id]
                else:
                    retrieved_file: FileObject = await self.client.files.retrieve(
                        citation.file_id
                    )
                    self.files_cache[citation.file_id] = retrieved_file
                filename = retrieved_file.filename
                if ".pdf" in filename:
                    filename = filename[:-4]
                elif ".md" in filename:
                    filename = filename[:-3]
                citation.file_id = filename
            except Exception as e:
                logger.error(f"Error retrieving file: {e}")
                # Keep the file_id the same, carry on

            self.citations.append(citation)

    @staticmethod
    def has_quote(annotation):
        return (
                annotation.file_citation.quote is not None
                and annotation.file_citation.quote != ""
        )

    def get_content(self) -> str:
        """
        Replace the annotation citation reference with an [n] type reference instead
        """
        value: str = self.message.content[0].text.value

        for i, annotation in enumerate(self.annotations):
            # Construct the citation reference, e.g., "[1]"
            citation_ref = f"[{len(self.annotations) - i}] "

            # Replace the citation text with the citation reference
            # Since we're working backward, we don't need to adjust the start and end indices

            value = (
                    value[: annotation.start_index]
                    + citation_ref
                    + value[annotation.end_index:]
            )

        # Add the footnotes
        value += self.get_elements()

        return value

    def set_elements(self) -> None:
        self.elements = []
        for i, citation in enumerate(self.citations, start=1):
            self.elements.append(f"{i} {citation.file_id}")

    def get_elements(self) -> str:
        current_message = self.message.content[0].text.value
        citation_text = '\n'
        last_source = ''
        for element in self.elements:
            index = element.split(' ')[0]
            source = element.split(' ', 1)[1]

            # If the source we just used is the same as the source we are finding now
            if last_source == source:
                # Find the citation we just made
                last_bracket_pos = citation_text.rfind(']')
                # Add our citation. Ex: [1][2] filename
                citation_text = citation_text[:last_bracket_pos + 1] + ' ' + '[' + index + ']' + citation_text[
                                                                                         last_bracket_pos + 1:]
            else:
                # For new citations, just add the citation. Ex: [1] filename
                citation_text += '\n' + f"*[{index}] {source}*"
                last_source = source
        return citation_text

    def get_message(self) -> Message:
        return Message(content=self.get_content(), elements=self.get_elements())

    async def main(self) -> None:
        if not self.has_annotations():
            return
        if self.validate_indexes():
            await self.set_citations()
            self.set_elements()
            self.get_content()
            self.get_elements()
        else:
            logger.error(f"Error validating message annotations index: {self._id}")
        return
