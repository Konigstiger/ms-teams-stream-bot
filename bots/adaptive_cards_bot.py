# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import base64
import datetime
import json
import os
import random

from botbuilder.core import ActivityHandler, TurnContext, CardFactory, StatePropertyAccessor, ConversationState, \
    UserState
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus
from botbuilder.schema import ChannelAccount, Attachment, Activity, ActivityTypes, ConversationAccount

CARDS = [
    "resources/VideoCard.json"

]


class AdaptiveCardsBot(ActivityHandler):
    """
    This bot will respond to the user's input with an Adaptive Card. Adaptive Cards are a way for developers to
    exchange card content in a common and consistent way. A simple open card format enables an ecosystem of shared
    tooling, seamless integration between apps, and native cross-platform performance on any device. For each user
    interaction, an instance of this class is created and the OnTurnAsync method is called.  This is a Transient
    lifetime service. Transient lifetime services are created each time they're requested. For each Activity
    received, a new instance of this class is created. Objects that are expensive to construct, or have a lifetime
    beyond the single turn, should be carefully managed.
    """

    def __init__(
            self,
            conversation_state: ConversationState,
            user_state: UserState,
            dialog: Dialog,
    ):
        if conversation_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. user_state is required but None was given"
            )
        if dialog is None:
            raise Exception(
                "[DialogBot]: Missing parameter. dialog is required"
            )

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        self.user_state_accessor = self.user_state.create_property(
            "WelcomeUserState"
        )
        self.WELCOME_MESSAGE = """Hello user!"""

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello user!")

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have ocurred during the turn.
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Respond to messages sent from the user.
        """
        await self.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )

    @staticmethod
    async def run_dialog(
        dialog: Dialog,
        turn_context: TurnContext,
        accessor: StatePropertyAccessor,
    ):
        dialog_set = DialogSet(accessor)
        dialog_set.add(dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        results = await dialog_context.continue_dialog()
        if results.status == DialogTurnStatus.Empty:
            await dialog_context.begin_dialog(dialog.id)
