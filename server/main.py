import yaml
import os
from telegram.ext import Updater, \
                         CommandHandler, \
                         ConversationHandler, \
                         CallbackQueryHandler, \
                         CallbackContext
from telegram import InlineKeyboardMarkup, \
                     InlineKeyboardButton, \
                     Update
from google.oauth2 import service_account
from gcp.check_vm import list_all_instances, \
                         format_instance_info, \
                         format_instance_info_dynamic
from gcp.rm_vm import delete_instance

with open('assets/config.yaml', 'r') as file:
    data = yaml.safe_load(file)

GCP_PROJECT_ID = data.get('GCP_PROJECT_ID')
GCP_ZONE = data.get('GCP_ZONE')
GCP_SERVICE_ACCOUNT_KEY_PATH = data.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
TELEGRAM_BOT_TOKEN = data.get('TELEGRAM_BOT_TOKEN')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_SERVICE_ACCOUNT_KEY_PATH

# credentials = service_account.Credentials.from_service_account_file(
#     GCP_SERVICE_ACCOUNT_KEY_PATH,
#     scopes=["https://www.googleapis.com/auth/cloud-platform"],
# )

def check_vm(update: Update, context: CallbackContext) -> None:
    result = list_all_instances(GCP_PROJECT_ID)
    result = format_instance_info(result)
    update.message.reply_text(result)

CHOOSING, OPTION_SELECTED, VM_ACTION_SELECTED = range(3)

def vm_functions(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Check VM", callback_data='1')],
        [InlineKeyboardButton("Remove VM", callback_data='2')],
        [InlineKeyboardButton("Create VM", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose one:', reply_markup=reply_markup)
    return CHOOSING

def vm_action_click(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    sub_option_selected = query.data
    context.user_data['sub_option_selected'] = sub_option_selected
    if sub_option_selected == 'Cancel':
        query.edit_message_text('Cancel this time action.')
        return ConversationHandler.END

    query.edit_message_text(f'Start to deleteing {sub_option_selected}... Please wait for a bit.')
    res = delete_instance(GCP_PROJECT_ID, 'asia-east1-b', sub_option_selected)
    if res:
        reply_text = f'Done to delete the {sub_option_selected} VM on GCP.'
    else:
        reply_text = f'Fail to delete the VM {sub_option_selected}'
    query.edit_message_text(reply_text)
    return ConversationHandler.END

def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    option_selected = query.data
    # context.user_data['selected_option'] = option_selected

    result = list_all_instances(GCP_PROJECT_ID)
    result_1 = format_instance_info(result)
    result_2 = format_instance_info_dynamic(result)

    if option_selected == '1':
        query.edit_message_text(result_1)
    elif option_selected == '2':
        dynamic_buttons = []
        for i, element in enumerate(result_2):
           dynamic_buttons.append({"text": element,  
                                   "callback_data": element})
        # Add one more button for Cancel this time action. 
        dynamic_buttons.append({"text": "Cancel",  "callback_data": "Cancel"})

        keyboard = [InlineKeyboardButton(button["text"],
                                         callback_data=button["callback_data"]) for button in dynamic_buttons]
        reply_markup = InlineKeyboardMarkup([keyboard])
        query.edit_message_text('Please choose a VM:', reply_markup=reply_markup)
        return VM_ACTION_SELECTED
    elif option_selected == '3':
        query.edit_message_text('Do not support the function of creating VM.')
    return ConversationHandler.END


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add the command in this handler
    # dispatcher.add_handler(CommandHandler("check_vm", check_vm))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('gcp_vm', vm_functions)],
        states={
            CHOOSING: [CallbackQueryHandler(button_click)],
            VM_ACTION_SELECTED: [CallbackQueryHandler(vm_action_click)],
            OPTION_SELECTED: [],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)

    # Start Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':

    main()
