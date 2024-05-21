"""
Map OpenAI's ThreadMessage to Chainlit's Message objects.

We check for file annotation, and do some modification to the content to format reference notes.

We've had a lot of bugs with OpenAI's annotations, so we have to validate the indexes to make sure we don't do substitutions on the wrong indexes, or have missing annotations.

"""
from chainlit import Message
from chainlit.element import Text
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
                retrieved_file: FileObject = await self.client.files.retrieve(
                    annotation.file_citation.file_id
                )
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
        value: str = self.message.content[0].text.value

        for i, annotation in enumerate(self.annotations):
            # Construct the citation reference, e.g., "[1]"
            citation_ref = f"[{len(self.annotations) - i}]"

            # Replace the citation text with the citation reference
            # Since we're working backward, we don't need to adjust the start and end indices)

            if self.has_quote(annotation):
                value = (
                        value[: annotation.start_index]
                        + citation_ref
                        + value[annotation.end_index:]
                )
            else:  # We've got a bug, OAI forgot to return the citation, so remove the reference
                value = value[: annotation.start_index] + value[annotation.end_index:]

        return value

    def set_elements(self) -> None:
        self.elements = [
            (
                f"[{i}] {citation.file_id}",
                f"{citation.quote if citation.quote else ' '}",  # Can't be '' needs have the space
            )
            for i, citation in enumerate(self.citations, start=1)
        ]

    def get_elements(self) -> list[Text]:
        cl_text: list[Text] = []
        for element in self.elements:
            cl_text.append(Text(name=element[0], content=element[1], display="inline"))
        return cl_text

    def get_message(self) -> Message:
        return Message(content=self.get_content(), elements=self.get_elements())

    async def main(self) -> None:
        if not self.has_annotations():
            return
        if self.validate_indexes():
            await self.set_citations()
            self.get_content()
            self.set_elements()
        else:
            logger.error(f"Error validating message annotations index: {self._id}")
        return
