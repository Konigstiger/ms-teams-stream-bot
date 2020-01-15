import datetime
import json
import os
import random

from botbuilder.core import UserState, CardFactory
from botbuilder.dialogs import WaterfallDialog, ComponentDialog, ChoicePrompt, TextPrompt, ConfirmPrompt, \
    WaterfallStepContext, DialogTurnResult, PromptOptions
from botbuilder.schema import ChannelAccount, ConversationAccount, ActivityTypes, Activity, Attachment

from bots import AdaptiveCardsBot


class Dialog(ComponentDialog):
    """ TODO: Add description for OrderDialog class. """

    def __init__(self, user_state: UserState):
        super(Dialog, self).__init__(Dialog.__name__)
        self.user_profile_accesor = user_state.create_property("UserProfile")

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.options_step,
                ],
            )
        )
        self.add_dialog(ChoicePrompt("options_step"))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.add_dialog(TextPrompt(TextPrompt.__name__))


    @staticmethod
    def _create_adaptive_card_attachment() -> Attachment:
        """
        Load a random adaptive card attachment from file.
        :return:
        """
        card_path = os.path.join(os.getcwd(), "resources/VideoCard.json")
        with open(card_path, "rb") as in_file:
            card_data = json.load(in_file)

        return CardFactory.adaptive_card(card_data)

    async def options_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        card = self._create_adaptive_card_attachment()

        response = Dialog.create_activity_reply(
            step_context.context.activity, "", "", [card]
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=response)
        )

    @staticmethod
    def create_activity_reply(
        activity: Activity, text: str = None, locale: str = None, attachments=None
    ):
        if attachments is None:
            attachments = []
        attachments_aux = attachments.copy()

        return Activity(
            type=ActivityTypes.message,
            timestamp=datetime.datetime.utcnow(),
            from_property=ChannelAccount(
                id=getattr(activity.recipient, "id", None),
                name=getattr(activity.recipient, "name", None),
            ),
            recipient=ChannelAccount(
                id=activity.from_property.id, name=activity.from_property.name
            ),
            reply_to_id=activity.id,
            service_url=activity.service_url,
            channel_id=activity.channel_id,
            conversation=ConversationAccount(
                is_group=activity.conversation.is_group,
                id=activity.conversation.id,
                name=activity.conversation.name,
            ),
            text=text or "",
            locale=locale or "",
            attachments=attachments_aux,
            entities=[],
        )
