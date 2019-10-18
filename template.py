        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Menu',
                text='Please select',
                actions=[
                    MessageAction(
                        label='message',
                        text='message text'
                    ),
                    MessageAction(
                        label='message2',
                        text='message text2'
                    )
                ]
            )
        )
