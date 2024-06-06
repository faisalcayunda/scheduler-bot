from telegram.ext import CommandHandler, MessageHandler, filters, Application
from credentials import  TOKEN, BOT_USERNAME
from handlers import start_command, handle_message, get_list, check_status, regenerate_password, error



app = Application.builder().token(TOKEN).build()

# Add command handlers
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("list", get_list))
app.add_handler(CommandHandler("checkstatus", check_status))
app.add_handler(CommandHandler("generatepassword", regenerate_password))

app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.add_error_handler(error)

if __name__ == "__main__":  
    print(f"BOT {BOT_USERNAME} started")
    app.run_polling(poll_interval=5)