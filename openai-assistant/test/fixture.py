from openai.types.beta.threads import (
    Text, Message, TextContentBlock
)
from openai.types.beta.threads.file_citation_annotation import FileCitation, FileCitationAnnotation

# VALID, SHOULD RENDER FINE
message_with_citation = Message.model_construct(
    id='message_with_citation',
    assistant_id='test_fixtures',
    content=[
        TextContentBlock(
            text=Text.model_construct(
                annotations=[FileCitationAnnotation(
                    end_index=241,
                    file_citation=FileCitation(
                        file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                        quote='Section 2 - Annual Leave\nA. Annual leave is provided to allow employees extended leave for rest\nand recreation and to provide periods of time off for personal and\nunscheduled purposes. All employees may request at least two consecutive\nweeks of annual leave per year and take such leave subject to the\nDepartment’s approval. \n\n\nDepartment of Veterans Affairs Labor Management Relations | DVA /AFGE Master Agreement 187\n\nEMPLOYEE RIGHTS AND PRIVILEGES | ARTICLE 35 - TIME AND LEAVE\n\n\nB. The use of accrued annual leave is an absolute right of the employee \nsubject to the right of the Department to approve when leave may'),
                    start_index=230,
                    text='【11†source】',
                    type='file_citation')],
                value='Certainly, the information regarding annual leave comes from the Department of Veterans Affairs Labor Management Relations and the DVA/AFGE Master Agreement, specifically under ARTICLE 35 - TIME AND LEAVE, Section 2 - Annual Leave【11†source】.'),
            type='text')],
    created_at=1705592604,
    file_ids=[],
    metadata={},
    object='thread.message',
    role='assistant',
    run_id='run_P0VLp3EnfewWCy2YcX2LYxIA',
    thread_id='thread_5C8BE2EGL4JYlpKBLNM1PaiS'
)

message_with_invalid_index = Message.model_construct(
    id='message_with_invalid_index',
    assistant_id='test_fixtures',
    content=[
        TextContentBlock(text=Text(annotations=[
            FileCitationAnnotation(end_index=258,
                                   file_citation=FileCitation(
                                       file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                                       quote='Section 1 - General\nA. Compensation is excluded from negotiation under 38 USC 7422'),
                                   start_index=247, text='ce】.',
                                   type='file_citation')],
            value='My apologies for any confusion. Here is the citation of the source from which I found the information:\n\nVA/AFGE Master Agreement (2023), Section 1 - General, Paragraph A states: "Compensation is excluded from negotiation under 38 USC 7422"【11†source】.'),
            type='text')], created_at=1706801495, file_ids=[],
    metadata={}, object='thread.message', role='assistant',
    run_id='run_9SWRbFyipzqTckDcBnq8RSRF',
    thread_id='thread_XiYxyBLx049tEb6ub6XPdonS')

message_no_citation = Message.model_construct(id='msg_GL9XTpzwoo3XBWTQePtRjraw',
                                              assistant_id='asst_UdBAhFZsmVSJCJ8THgCpA1tK',
                                              content=[TextContentBlock(text=Text(annotations=[],
                                                                                  value='Acknowledged. The system is ready to assist you. How can I help you today?'),
                                                                        type='text')], created_at=1706122266,
                                              file_ids=[],
                                              metadata={}, object='thread.message', role='assistant',
                                              run_id='run_iOOpi2eDMKqyyZ8hFNwx4kjw',
                                              thread_id='thread_GT9TMUClpNDcSdeObqst8yIP')

message_with_missing_quote_annotation = Message.model_construct(
    id='message_with_missing_quote_annotation',
    assistant_id='test_fixtures',
    content=[TextContentBlock(
        text=Text(
            annotations=[FileCitationAnnotation(
                end_index=330,
                file_citation=FileCitation(
                    file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                    quote='',
                ),
                start_index=319,
                text=' ',
                type='file_citation'
            )],
            value="If you need to leave work early due to an emergency, it is not specified that you have to enter a formal leave request. However, the procedures for unplanned leave—including leaving due to an emergency—usually require that you contact your supervisor or designee to request the leave. If the leave is to begin immediately, you should inform your supervisor or their designee, and you will be informed whether the leave is approved or disapproved at the time it is requested【5:5†VA-AFGE-2023-Master-Agreement】. It is important that during the operational hours of your facility, you rea out to someone who has the authority to receive and act upon your request.\n\nAdditionally, it's worth noting that for emergency annual leave, approval is generally granted when conditions warrant, but this is considered on an individual basis . \n\nTherefore, while you might not need to enter a formal request, you should still notify your supervisor as soon as possible to ensure that your leave is properly documented and approved."
        ),
        type='text'
    )],
    created_at=1711128199,
    file_ids=[],
    metadata={},
    object='thread.message',
    role='assistant',
    run_id='run_MJZ6wpn2Rl8k76ZjvZvJ6dTi',
    thread_id='thread_9U55LSxsPM95cS6eXBEVjNHS'
)

message_with_multiple_annotations_no_quotes = Message.model_construct(
    id='message_with_multiple_annotations',
    assistant_id='test_fixtures',
    content=[
        TextContentBlock(
            text=Text(annotations=[FileCitationAnnotation(end_index=649,
                                                          file_citation=FileCitation(
                                                              file_id='file-80O35GgEFpRE38EhT2HYe6qt',
                                                              quote=''), start_index=612,
                                                          text='【11:0†Supplemental Agreement - Other】',
                                                          type='file_citation'),
                                   FileCitationAnnotation(end_index=980,
                                                          file_citation=FileCitation(
                                                              file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                                                              quote=''), start_index=944,
                                                          text='【11:2†VA-AFGE-2023-Master-Agreement】',
                                                          type='file_citation'),
                                   FileCitationAnnotation(end_index=1301,
                                                          file_citation=FileCitation(
                                                              file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                                                              quote=''), start_index=1265,
                                                          text='【11:4†VA-AFGE-2023-Master-Agreement】',
                                                          type='file_citation')],
                      value="The Master Agreement addresses emergency leave in the context of annual leave for emergency reasons. It stipulates that when annual leave is requested, there will generally be a requirement for two weeks' notice to employees needed to cover a shift, except in cases of emergency annual leave. Emergency annual leave requests submitted after posted individual Service deadlines for requesting planned annual leave will be considered if one (1) month prior notice has been given. Approval of annual leave for emergency reasons will be considered on an individual basis and generally granted when conditions warrant【11:0†Supplemental Agreement - Other】. \n\nFurthermore, under the VA-AFGE 2023 Master Agreement, unplanned leave, which may cover emergency situations, requires that employees must contact their supervisor or designee to request leave. The employee will be informed whether leave is approved or disapproved at the time it is requested【11:2†VA-AFGE-2023-Master-Agreement】. \n\nFor those impacted by hazardous weather or emergency conditions, the Department and local union jointly plan procedures and communicate these to employees annually. The appropriate Department official informs the local union when hazardous weather/emergency conditions are declared【11:4†VA-AFGE-2023-Master-Agreement】. \n\nWhile specifics about emergency leave are discussed in these contexts, the agreement allows for negotiation and individual consideration, especially in emergency circumstances."),
            type='text')], created_at=1711384977, file_ids=[], metadata={}, object='thread.message',
    role='assistant', run_id='run_BwCbncan9K7k9BvjLAmDynk8',
    thread_id='thread_bN7e6WVAa4WiJP1dXT0AeNkR')

message_with_multiple_annotations = ThreadMessage(
    id='message_with_multiple_annotations',
    assistant_id='test_fixtures',
    content=[
        MessageContentText(
            text=Text(annotations=[TextAnnotationFileCitation(end_index=649,
                                                              file_citation=TextAnnotationFileCitationFileCitation(
                                                                  file_id='file-80O35GgEFpRE38EhT2HYe6qt',
                                                                  quote='Quote goes here'), start_index=612,
                                                              text='【11:0†Supplemental Agreement - Other】',
                                                              type='file_citation'),
                                   TextAnnotationFileCitation(end_index=980,
                                                              file_citation=TextAnnotationFileCitationFileCitation(
                                                                  file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                                                                  quote='Quote goes here'), start_index=944,
                                                              text='【11:2†VA-AFGE-2023-Master-Agreement】',
                                                              type='file_citation'),
                                   TextAnnotationFileCitation(end_index=1301,
                                                              file_citation=TextAnnotationFileCitationFileCitation(
                                                                  file_id='file-NHlneG03h2SdhS8Qzab5dbMw',
                                                                  quote='Quote goes here'), start_index=1265,
                                                              text='【11:4†VA-AFGE-2023-Master-Agreement】',
                                                              type='file_citation')],
                      value="The Master Agreement addresses emergency leave in the context of annual leave for emergency reasons. It stipulates that when annual leave is requested, there will generally be a requirement for two weeks' notice to employees needed to cover a shift, except in cases of emergency annual leave. Emergency annual leave requests submitted after posted individual Service deadlines for requesting planned annual leave will be considered if one (1) month prior notice has been given. Approval of annual leave for emergency reasons will be considered on an individual basis and generally granted when conditions warrant【11:0†Supplemental Agreement - Other】. \n\nFurthermore, under the VA-AFGE 2023 Master Agreement, unplanned leave, which may cover emergency situations, requires that employees must contact their supervisor or designee to request leave. The employee will be informed whether leave is approved or disapproved at the time it is requested【11:2†VA-AFGE-2023-Master-Agreement】. \n\nFor those impacted by hazardous weather or emergency conditions, the Department and local union jointly plan procedures and communicate these to employees annually. The appropriate Department official informs the local union when hazardous weather/emergency conditions are declared【11:4†VA-AFGE-2023-Master-Agreement】. \n\nWhile specifics about emergency leave are discussed in these contexts, the agreement allows for negotiation and individual consideration, especially in emergency circumstances."),
            type='text')], created_at=1711384977, file_ids=[], metadata={}, object='thread.message',
    role='assistant', run_id='run_BwCbncan9K7k9BvjLAmDynk8',
    thread_id='thread_bN7e6WVAa4WiJP1dXT0AeNkR')

message_with_no_quote = ThreadMessage(
    id='msg_yBtMOMDop6UBg5d9QfcyszSH',
    assistant_id='asst_UdBAhFZsmVSJCJ8THgCpA1tK',
    content=[MessageContentText(text=Text(annotations=[TextAnnotationFileCitation(end_index=799,
                                                                                  file_citation=TextAnnotationFileCitationFileCitation(
                                                                                      file_id='file-80O35GgEFpRE38EhT2HYe6qt',
                                                                                      quote=''), start_index=762,
                                                                                  text='【11:0†Supplemental Agreement - Other】',
                                                                                  type='file_citation')],
                                          value='The policy on emergency leave, specifically in the context of annual leave requested for emergency reasons, is outlined in the Supplemental Agreement - Other. It states that approval of annual leave for emergency reasons will be considered on an individual basis and generally granted when conditions warrant. This is applicable when annual leave is requested by personnel on established tours of duty where limited personnel are available, and the shifts must be covered. Typically, there is a two-week notice required for employees to cover a shift except for emergency annual leave. However, leave requests submitted after posted individual Service deadlines for requesting planned annual leave will also be considered if one-month prior notice has been given【11:0†Supplemental Agreement - Other】.'),
                                type='text')], created_at=1713369819, file_ids=[], metadata={}, object='thread.message',
    role='assistant', run_id='run_NLuWvTH6jB8bRDDUdnA6GYFj',
    thread_id='thread_3VUqa6OrkWXM98qIlpjWnmv7')

raw_user_data = {'id': '1234567890', 'email': 'testuser@nowhere.com', 'verified_email': True,
                 'name': 'Test User', 'given_name': 'Test', 'family_name': 'Users', 'picture': '',
                 'locale': 'en'}

citation = TextAnnotationFileCitationFileCitation(
    file_id='file-uYryyZwgG9RMrg0CLfsUijYX',
    quote='Annual leave is provided to allow employees extended leave for rest\nand recreation and to provide periods of time off for personal and\nunscheduled purposes. All employees may request at least two consecutive\nweeks of annual leave per year and take such leave subject to the\nDepartment’s approval')
