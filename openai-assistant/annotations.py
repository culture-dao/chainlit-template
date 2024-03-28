from chainlit.element import Text
from chainlit.logger import logger
from chainlit.message import Message
from openai.types.beta.threads import ThreadMessage


def construct_value_with_citations(message):
    value = message.content[0].text.value
    # Sort annotations by start_index to ensure replacements are done in the correct order
    sorted_annotations = sorted(message.content[0].text.annotations, key=lambda x: x.start_index, reverse=True)

    for i, annotation in enumerate(sorted_annotations):
        # Construct the citation reference, e.g., "[1]"
        citation_ref = f"[{len(sorted_annotations) - i}]"

        # Replace the citation text with the citation reference
        # Since we're working backward, we don't need to adjust the start and end indices
        value = value[:annotation.start_index] + citation_ref + value[annotation.end_index:]

    return value


def create_annotations_list(citations):
    """
    This function cannot be called outside a chainlit context
    """
    annotations = [
        Text(
            name=f"[{i}] {citation['name']}",
            content=f"{citation['quote'] if citation['quote'] else 'No quote available'}",
            display="inline")
        for i, citation in enumerate(citations, start=1)
    ]
    return annotations


def extract_citations(message):
    # Step 1: Extract citations
    citations = []
    for annotation in message.content[0].text.annotations:
        citation_name = annotation.text[annotation.text.find('†') + 1:annotation.text.find('】')]
        citation_details = {
            "file_id": annotation.file_citation.file_id,
            "quote": annotation.file_citation.quote,
            "name": citation_name
        }
        citations.append(citation_details)

    return citations


def has_annotations(message):
    return bool(message.content[0].text.annotations)


def build_message_with_annotations(message: ThreadMessage) -> Message:
    value = message.content[0].text.value

    if not has_annotations(message):
        return Message(content=value, elements=[])

    # Extract citations from the thread message
    citations = extract_citations(message)

    # Construct the message value with simplified citation references
    if validate_indexes(message):
        value = construct_value_with_citations(message)
    else:
        logger.error(f"Error validating message annotations: {message}")

    # Create annotations list for the citations
    annotations = create_annotations_list(citations)

    return Message(content=value, elements=annotations)


def validate_indexes(message):
    value = message.content[0].text.value
    for annotation in message.content[0].text.annotations:
        citation = value[annotation.start_index:annotation.end_index].strip()
        if citation[0] != '【' or citation[-1] != '】':
            return False
    return True
