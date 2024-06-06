from telegram import Update
from telegram.ext import ContextTypes
from credentials import BOT_USERNAME
import json, httpx, secrets, string
from datetime import datetime

urls:dict = json.load(open("./data/replikasi.json"))

def handle_response(text: str) -> str:
    text = text.lower()

    if "hi" in text:
            return "Haloo!"

    elif "apa kabar" in text:
        return "Baik."

    else:
        return "Saya tidak mengerti maksudnya."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Halo {update.message.from_user.first_name}, bot sudah berjalan loh!')
    
async def get_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temp = list(urls.keys())
    message = ""
    for i in range(len(temp)):
        message += "{:<5}{:<20}\n".format(str(i+1)+".", temp[i])
        
    await update.message.reply_text(message)
    
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = ""
    message = ""
    index = 1
    args = context.args
    
    await update.message.reply_text("Mohon tunggu, di check dulu ya!")
    
    async with httpx.AsyncClient(verify=False) as client:
        if not args:
            for key, value in urls.items():
                url = value["url"]
                response = await client.get(url=url)
                if response.status_code in {200}:
                    status = "✅"
                else:
                    status = "❌"
                message += "{:<5}{} - {}\n".format(str(index)+".", key, status)
                index += 1
            await update.message.reply_text(message)
        else:
            try:
                region = " ".join(args).title()
                url = urls[region]["url"]
                response = await client.get(url)
                if response.status_code in {200}:
                    status = "✅"
                else:
                    status = "❌"
                message += f"{region} - {status}"
            
                await update.message.reply_text(message)
            except KeyError:
                await update.message.reply_text("Kota/Kabupaten tidak terdaftar")
                
            
    
async def regenerate_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alpha = string.ascii_letters + string.digits
    new_password = "".join(secrets.choice(alpha) for _ in range(20))
    print("Generating new password: ", new_password)
    current_data = urls.copy()
    message = ""
    index = 1
    
    async with httpx.AsyncClient(verify=False) as client:
        for key, value in urls.items():
            url = value["url"]+"/api"
            admin_username = "prov_administrator"
            cur_password = value["password"]
            response = await client.post(url=url+"/auth/signin", json={"username":admin_username, "password":cur_password})
            if response.status_code == 200:
                try:
                    token = response.json()["data"]["jwt"]
                    response = await client.get(url=url+"/user/prov_administrator", headers={"Authorization": "Bearer "+token})
                    if response.status_code == 200:
                        json_data = {"password": new_password}
                        response = await client.put(url=url+"/user/prov_administrator", headers={"Authorization": "Bearer "+token}, json=json_data)
                        if response.status_code == 200:
                            print("Berhasil merubah password ", key)
                            current_data[key]["password"]= new_password
                            message += "{:<5}{} > {}\n".format(str(index)+".", key, new_password)
                        else:
                            print("Gagal merubah password ", key)
                            message += "{:<5}{} > {}\n".format(str(index)+".", key, cur_password)
                    else:
                        message += "{:<5}{} > {}\n".format(str(index)+".", key, cur_password)
                except KeyError:
                    message += "{:<5}{} > {}\n".format(str(index)+".", key, cur_password)
            else:
                message += "{:<5}{} > {}\n".format(str(index)+".", key, "Gagal mendapatkan akun prov")
            index += 1
                
        with open("./data/replikasi.json", "w") as data_file:
            with open(f"./dumps/{datetime.now().strftime()}", "w") as dump_file:
                json.dump(urls, dump_file, indent=6)
            
            json.dump(current_data, data_file,indent=6)
            
    await update.message.reply_text(message)
    

    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User ({update.message.chat.id})in {message_type}: "{text}"')
    print(f"Message Type: {message_type}")

    if message_type == 'group':
        if BOT_USERNAME in text:   
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            response = handle_response(new_text)
    else:
        response = handle_response(text)
    
    print('Bot:', response)
    await update.message.reply_text(response)
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    
