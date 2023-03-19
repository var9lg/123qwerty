"""парсер"""

import asyncio
import csv


async def main_parse_telegram(app, list_of_words):

    groups = []
    # list_of_words = ["привет", "тест"]

    async with app:
        """
        Get all groups of client
        """
        async for dialog in app.get_dialogs():
            # if str(dialog.chat.type) == 'ChatType.SUPERGROUP' or str(dialog.chat.type) == "ChatType.GROUP":
            if str(dialog.chat.type) == "ChatType.SUPERGROUP":

                groups.append(dialog.chat)

        """Get all chat history from telegram chats of all groups"""
        limit = 100
        total_messages = 0
        total_count_limit = 0
        group_list = []
        with open("TelegramParse/groups_file.txt", "r", encoding="UTF-8") as f:
            for line in f:
                line_lst = line.replace("\n", "").split()
                group_list.append([" ".join(line_lst[:-1]), int(line_lst[-1])])

        group_names_list = [group_list[i][0] for i in range(len(group_list))]

        while True:
            for g in groups:
                all_messages = set()
                if g.title in group_names_list:
                    iter_of_current_group = group_names_list.index(g.title)
                    max_index = group_list[iter_of_current_group][1]
                    offset_id = 0
                    i = 0
                    while True:
                        messages = []
                        async for message in app.get_chat_history(chat_id=g.id, limit=limit, offset_id=offset_id):
                            if message.id > group_list[iter_of_current_group][1]:
                                messages.append(message)
                        if not messages:
                            break
                        messages = messages[::-1]
                        for message in messages:
                            if not message.text:
                                continue
                            text_message = message.text
                            # list_of_words_mess = text_message.split()
                            for word in list_of_words:
                                if word in text_message:
                                    user_sended = message.from_user  # информация и юзере
                                    user_name = user_sended.username
                                    if not user_name:
                                        user_name = "None user tag"
                                    last_name = user_sended.last_name
                                    if not last_name:
                                        user_name = "None user lastname"
                                    tup_for_str = (
                                        text_message, g.title, (user_name, user_sended.first_name, last_name),
                                        message.date)
                                    if tup_for_str not in all_messages:
                                        with open("TelegramParse/chats.csv", "a", encoding="UTF-8") as f:
                                            writer = csv.writer(f, delimiter=",", lineterminator="\n")
                                            writer.writerow([text_message, g.title, user_name,
                                                             user_sended.first_name, last_name, message.date])
                                        all_messages.add(tup_for_str)
                                    break
                        offset_id = messages[0].id
                        if not i:
                            max_index = messages[-1].id
                        i += 1
                    group_list[iter_of_current_group][1] = max_index
            #             if total_count_limit != 0 and total_messages >= total_count_limit:
            #                 break
            with open("TelegramParse/groups_file.txt", "w", encoding="UTF-8") as f:
                for g in group_list:
                    f.write(f"{g[0]} {str(g[1])}\n")
            # print("Сохраняем данные в файл...")
            with open("TelegramParse/chats.csv", "a", encoding="UTF-8") as f:
                writer = csv.writer(f, delimiter=",", lineterminator="\n")
                for message in all_messages:
                    writer.writerow([message[0], message[1], f'{message[2][0]} ({" ".join(message[2][1:])})', message[3]])
            # print('Парсинг сообщений групп успешно выполнен.')

            # i += 1
            await asyncio.sleep(30)
            print("Итерация закончилась!")







