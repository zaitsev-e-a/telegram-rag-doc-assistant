import asyncio
import os
import uuid
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from core.config import settings
from memory.redis_history import clear_user_history
from pipeline.document_pipeline import process_document
from pipeline.message_pipeline import process_message
from storage.qdrant_search import delete_user_knowledge



def build_tmp_filename(original_name):
    suffix = ""
    if original_name:
        suffix = Path(original_name).suffix.lower()

    return f"{uuid.uuid4().hex}{suffix}"


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет! Я могу проанализировать файлы и отвечать на вопросы по их содержимому.\n\n"
        "Поддерживаемые форматы: pdf, docx, doc, txt.\n"
        "Сначала загрузи один или несколько файлов, затем задавай вопросы по ним."
    )
    await update.message.reply_text(text)


async def restart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id if update.effective_user else "unknown"

    clear_user_history(user_id)
    delete_user_knowledge(user_id)

    await update.message.reply_text(
        "Память очищена: история диалога и загруженные документы удалены.\n\n"
        "Перезагружаюсь."
    )

    text = (
        "Привет! Я могу проанализировать файлы и отвечать на вопросы по их содержимому.\n\n"
        "Поддерживаемые форматы: pdf, docx, doc, txt.\n"
        "Сначала загрузи один или несколько файлов, затем задавай вопросы по ним."
    )
    await update.message.reply_text(text)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id if update.effective_user else "unknown"
    answer = process_message(user_id=user_id, message_text=update.message.text)

    await update.message.reply_text(answer)


async def _process_single_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return

    user_id = update.effective_user.id if update.effective_user else "unknown"
    document = update.message.document
    original_name = document.file_name or "unknown_file"

    telegram_file = await document.get_file()

    tmp_name = build_tmp_filename(original_name)
    tmp_path = settings.TMP_DIR / tmp_name

    await telegram_file.download_to_drive(custom_path=str(tmp_path))

    try:
        result = process_document(
            file_path=str(tmp_path),
            user_id=user_id,
            source=original_name,
        )

        if not result["success"]:
            await update.message.reply_text(result["message"])
            return


        await update.message.reply_text(
            "\n".join(
                [
                    f"Файл обработан: {original_name}",
                    f"Тип файла: {result['file_type']}",
                ]
            )
        )

        caption = (update.message.caption or "").strip()
        if caption:
            await update.message.reply_text("Обрабатываю ваш вопрос к файлу...")

            answer = process_message(
                user_id=user_id,
                message_text=caption,
            )

            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(
                "Теперь можешь задавать вопросы по документу."
            )

    finally:
        if tmp_path.exists():
            os.remove(tmp_path)


async def _process_media_group(bot, chat_id: int, user_id: int | str, group_id: str, items: list[dict]) -> None:
    processed_files = []
    failed_files = []

    caption = ""
    for item in items:
        item_caption = (item.get("caption") or "").strip()
        if item_caption:
            caption = item_caption
            break

    for item in items:
        telegram_file = await bot.get_file(item["file_id"])
        original_name = item["file_name"] or "unknown_file"

        tmp_name = build_tmp_filename(original_name)
        tmp_path = settings.TMP_DIR / tmp_name

        await telegram_file.download_to_drive(custom_path=str(tmp_path))

        try:
            result = process_document(
                file_path=str(tmp_path),
                user_id=user_id,
                source=original_name,
            )

            if result["success"]:
                processed_files.append(
                    {
                        "name": original_name,
                        "file_type": result["file_type"],
                        "chunks_count": result["chunks_count"],
                        "summary_created": result.get("summary_created", False),
                    }
                )
            else:
                failed_files.append(
                    {
                        "name": original_name,
                        "error": result["message"],
                    }
                )
        finally:
            if tmp_path.exists():
                os.remove(tmp_path)

    if processed_files:
        lines = [
            f"Обработано файлов: {len(processed_files)}",
            "",
        ]

        for file_info in processed_files:
            lines.append(
                f"• {file_info['name']} | тип: {file_info['file_type']} | "
            )

        if failed_files:
            lines.append("")
            lines.append(f"Не удалось обработать файлов: {len(failed_files)}")
            for file_info in failed_files:
                lines.append(f"• {file_info['name']} | ошибка: {file_info['error']}")

        await bot.send_message(chat_id=chat_id, text="\n".join(lines))

        if caption:
            await bot.send_message(
                chat_id=chat_id,
                text="Все файлы обработаны. Обрабатываю ваш вопрос к группе файлов...",
            )

            answer = process_message(
                user_id=user_id,
                message_text=caption,
            )

            await bot.send_message(chat_id=chat_id, text=answer)
        else:
            await bot.send_message(
                chat_id=chat_id,
                text="Все файлы обработаны. Теперь можешь задавать вопросы по ним.",
            )

    else:
        lines = [
            "Не удалось обработать ни один файл из группы.",
        ]

        if failed_files:
            lines.append("")
            for file_info in failed_files:
                lines.append(f"• {file_info['name']} | ошибка: {file_info['error']}")

        await bot.send_message(chat_id=chat_id, text="\n".join(lines))


async def _delayed_media_group_worker(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int | str,
    group_id: str,
) -> None:
    await asyncio.sleep(settings.MEDIA_GROUP_DEBOUNCE_SECONDS)

    media_groups = context.application.bot_data.setdefault("media_groups", {})
    group_data = media_groups.pop(group_id, None)

    if not group_data:
        return

    await _process_media_group(
        bot=context.bot,
        chat_id=chat_id,
        user_id=user_id,
        group_id=group_id,
        items=group_data["items"],
    )


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return

    user_id = update.effective_user.id if update.effective_user else "unknown"
    media_group_id = update.message.media_group_id

    if not media_group_id:
        await _process_single_document_message(update, context)
        return

    media_groups = context.application.bot_data.setdefault("media_groups", {})
    group = media_groups.setdefault(
        media_group_id,
        {
            "items": [],
            "task_started": False,
            "chat_id": update.effective_chat.id if update.effective_chat else None,
            "user_id": user_id,
        },
    )

    group["items"].append(
        {
            "file_id": update.message.document.file_id,
            "file_name": update.message.document.file_name or "unknown_file",
            "caption": update.message.caption or "",
            "message_id": update.message.message_id,
        }
    )

    if not group["task_started"]:
        group["task_started"] = True

        asyncio.create_task(
            _delayed_media_group_worker(
                context=context,
                chat_id=group["chat_id"],
                user_id=group["user_id"],
                group_id=media_group_id,
            )
        )