from osis_common.messaging import message_config, send_message


def send_email(template_references, receivers, data, connected_user=None):
    message_content = message_config.create_message_content(
        template_references['html'],
        template_references['txt'],
        [],
        receivers,
        data['template'],
        data['subject'],
        data.get('attachment')
    )
    send_message.send_messages(
        message_content=message_content,
        connected_user=connected_user
    )
