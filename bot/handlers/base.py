from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Voice, Audio, Document
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import logging

from bot.database import db
from bot.keyboards.inline import get_main_menu_keyboard, get_translation_actions_keyboard
from bot.keyboards.reply import get_main_reply_keyboard
from bot.services.translator import TranslatorService
from bot.services.voice import VoiceService
from bot.utils.messages import get_text
from bot.utils.rate_limit import rate_limit
from config import config

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()

    # Add user to database
    user = message.from_user
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code or 'ru'
    )

    # Get user info
    user_info = await db.get_user(user.id)
    is_premium = user_info.get('is_premium', False)

    welcome_text = get_text('welcome', user_info.get('interface_language', 'ru'))

    await message.answer(
        welcome_text,
        reply_markup=get_main_reply_keyboard(is_premium)
    )

    await message.answer(
        get_text('main_menu', user_info.get('interface_language', 'ru')),
        reply_markup=get_main_menu_keyboard(is_premium)
    )

@router.message(Command("help", "помощь"))
async def help_handler(message: Message):
    """Handle help command"""
    user_info = await db.get_user(message.from_user.id)
    help_text = get_text('help', user_info.get('interface_language', 'ru'))

    await message.answer(help_text)

@router.message(Command("premium", "премиум"))
async def premium_handler(message: Message):
    """Handle premium command"""
    user_info = await db.get_user(message.from_user.id)

    if user_info.get('is_premium'):
        premium_text = get_text('already_premium', user_info.get('interface_language', 'ru'))
    else:
        premium_text = get_text('premium_info', user_info.get('interface_language', 'ru'))

    await message.answer(premium_text)

@router.message(Command("language", "язык"))
async def language_handler(message: Message):
    """Handle language selection command"""
    from bot.keyboards.inline import get_language_selection_keyboard

    user_info = await db.get_user(message.from_user.id)
    current_lang = user_info.get('target_language', 'en')

    text = get_text('select_language', user_info.get('interface_language', 'ru')).format(
        current_lang=config.SUPPORTED_LANGUAGES.get(current_lang, current_lang)
    )

    await message.answer(text, reply_markup=get_language_selection_keyboard())

@router.message(Command("style", "стиль"))
async def style_handler(message: Message):
    """Handle style selection command"""
    from bot.keyboards.inline import get_style_selection_keyboard

    user_info = await db.get_user(message.from_user.id)
    current_style = user_info.get('translation_style', 'informal')

    text = get_text('select_style', user_info.get('interface_language', 'ru')).format(
        current_style=config.TRANSLATION_STYLES.get(current_style, current_style)
    )

    await message.answer(text, reply_markup=get_style_selection_keyboard())

@router.message(Command("settings", "настройки"))
async def settings_handler(message: Message):
    """Handle settings command"""
    from bot.keyboards.inline import get_settings_keyboard

    user_info = await db.get_user(message.from_user.id)
    text = get_text('settings_menu', user_info.get('interface_language', 'ru'))

    await message.answer(text, reply_markup=get_settings_keyboard(user_info))

@router.message(Command("history", "история"))
async def history_handler(message: Message):
    """Handle history command"""
    user_info = await db.get_user(message.from_user.id)

    if not user_info.get('is_premium'):
        await message.answer(get_text('premium_required', user_info.get('interface_language', 'ru')))
        return

    # Get recent history
    history = await db.get_user_history(message.from_user.id, limit=10)

    if not history:
        await message.answer(get_text('no_history', user_info.get('interface_language', 'ru')))
        return

    text = get_text('history_header', user_info.get('interface_language', 'ru')) + "\n\n"

    for item in history:
        text += f"🔸 {item['source_text'][:50]}{'...' if len(item['source_text']) > 50 else ''}\n"
        text += f"   → {item['translated_text'][:50]}{'...' if len(item['translated_text']) > 50 else ''}\n"
        text += f"   📅 {item['created_at'][:19]}\n\n"

    from bot.keyboards.inline import get_history_keyboard
    await message.answer(text, reply_markup=get_history_keyboard())

@router.message(F.voice)
@rate_limit(key='voice', rate=5, per=60)
async def voice_handler(message: Message):
    """Handle voice messages"""
    user_info = await db.get_user(message.from_user.id)

    # Check if user can use voice features
    if not user_info.get('is_premium'):
        await message.answer(get_text('voice_premium_required', user_info.get('interface_language', 'ru')))
        return

    # Check daily limit for free users (voice counts as translation)
    can_translate, remaining = await db.check_daily_limit(message.from_user.id)
    if not can_translate:
        await message.answer(get_text('daily_limit_reached', user_info.get('interface_language', 'ru')))
        return

    # Show processing message
    processing_msg = await message.answer(get_text('processing_voice', user_info.get('interface_language', 'ru')))

    try:
        async with VoiceService() as voice_service:
            # Process voice message
            text = await voice_service.process_voice_message(message.voice.file_id, message.bot)

            if not text:
                await processing_msg.edit_text(get_text('voice_processing_failed', user_info.get('interface_language', 'ru')))
                return

            # Translate the transcribed text
            async with TranslatorService() as translator:
                target_lang = user_info.get('target_language', 'en')
                style = user_info.get('translation_style', 'informal')

                translated, metadata = await translator.translate(
                    text=text,
                    target_lang=target_lang,
                    style=style,
                    enhance=user_info.get('is_premium', False)
                )

                if not translated:
                    await processing_msg.edit_text(get_text('translation_failed', user_info.get('interface_language', 'ru')))
                    return

                # Update counters
                await db.increment_translation_count(message.from_user.id)
                await db.add_translation_history(
                    user_id=message.from_user.id,
                    source_text=text,
                    source_language=metadata.get('source_lang'),
                    translated_text=translated,
                    target_language=target_lang,
                    style=style,
                    is_voice=True
                )

                # Format response
                response_text = f"🎤 *Распознано:* {text}\n\n"

                # Show both translation stages for premium users
                if 'basic_translation' in metadata and user_info.get('is_premium', False):
                    response_text += f"📝 *Точный перевод:*\n{metadata['basic_translation']}\n\n"
                    response_text += f"✨ *Улучшенный перевод (GPT-4o):*\n{translated}"

                    # Add synonyms/alternatives if available
                    if metadata.get('alternatives'):
                        response_text += f"\n\n🔄 *Альтернативы:*\n"
                        for alt in metadata['alternatives'][:2]:  # Show max 2 alternatives
                            response_text += f"• {alt}\n"

                    # Add explanation if available
                    if metadata.get('explanation') and metadata['explanation'].strip():
                        explanation = metadata['explanation'].strip()[:150]  # Shorter for voice
                        response_text += f"\n💡 *Объяснение:* {explanation}"
                        if len(metadata['explanation']) > 150:
                            response_text += "..."
                else:
                    response_text += f"🌍 *Перевод ({config.SUPPORTED_LANGUAGES.get(target_lang, target_lang)}):*\n{translated}"

                # Store metadata for callback buttons
                if user_info.get('is_premium', False):
                    from bot.handlers.callbacks import last_translation_metadata
                    last_translation_metadata[message.from_user.id] = metadata

                await processing_msg.edit_text(
                    response_text,
                    parse_mode='Markdown',
                    reply_markup=get_translation_actions_keyboard(True, user_info.get('is_premium', False))
                )

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await processing_msg.edit_text(get_text('voice_processing_failed', user_info.get('interface_language', 'ru')))

@router.message(F.text & ~F.text.startswith('/'))
@rate_limit(key='translation', rate=10, per=60)
async def text_translation_handler(message: Message):
    """Handle text translation"""
    user_info = await db.get_user(message.from_user.id)

    # Handle keyboard button presses
    if message.text == '🌍 Язык':
        await language_handler(message)
        return
    elif message.text == '🎨 Стиль':
        await style_handler(message)
        return
    elif message.text == '⚙️ Настройки':
        await settings_handler(message)
        return
    elif message.text == '❓ Помощь':
        await help_handler(message)
        return
    elif message.text == '📚 История':
        await history_handler(message)
        return
    elif message.text == '📄 Экспорт':
        # Handle export request
        user_info = await db.get_user(message.from_user.id)
        if not user_info.get('is_premium'):
            await message.answer(get_text('premium_required', user_info.get('interface_language', 'ru')))
            return
        from bot.keyboards.inline import get_export_keyboard
        await message.answer(
            get_text('select_export_format', user_info.get('interface_language', 'ru')),
            reply_markup=get_export_keyboard()
        )
        return
    elif message.text == '⭐ Премиум':
        await premium_handler(message)
        return

    # Check daily limit
    can_translate, remaining = await db.check_daily_limit(message.from_user.id)
    if not can_translate:
        limit_text = get_text('daily_limit_reached', user_info.get('interface_language', 'ru'))
        await message.answer(limit_text)
        return

    # Show typing
    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')

    try:
        async with TranslatorService() as translator:
            target_lang = user_info.get('target_language', 'en')
            style = user_info.get('translation_style', 'informal')

            # Check if user is admin and should get premium features
            from config import config
            is_admin = message.from_user.id == config.ADMIN_ID
            has_premium = user_info.get('is_premium', False) or is_admin

            logger.info(f"Translation for user {message.from_user.id}: admin={is_admin}, premium={has_premium}")

            translated, metadata = await translator.translate(
                text=message.text,
                target_lang=target_lang,
                style=style,
                enhance=has_premium
            )

            if not translated:
                await message.answer(get_text('translation_failed', user_info.get('interface_language', 'ru')))
                return

            # Update counters
            logger.info("Starting database updates...")
            await db.increment_translation_count(message.from_user.id)
            await db.add_translation_history(
                user_id=message.from_user.id,
                source_text=message.text,
                source_language=metadata.get('source_lang'),
                translated_text=translated,
                target_language=target_lang,
                style=style,
                is_voice=False
            )
            logger.info("Database updates completed")

            # Format response
            logger.info(f"Getting language names: source={metadata.get('source_lang', 'auto')}, target={target_lang}")
            source_lang_name = await translator.get_language_name(
                metadata.get('source_lang', 'auto'),
                user_info.get('interface_language', 'ru')
            )
            logger.info(f"Source language name: {source_lang_name}")
            target_lang_name = await translator.get_language_name(
                target_lang,
                user_info.get('interface_language', 'ru')
            )
            logger.info(f"Target language name: {target_lang_name}")

            response_text = f"🌍 *{source_lang_name} → {target_lang_name}*\n\n"

            # Debug logging for translation display
            basic_trans = metadata.get('basic_translation', 'N/A')
            logger.info(f"Translation display logic: basic='{basic_trans[:50]}...', enhanced='{translated[:50]}...', same={basic_trans == translated}")
            logger.info(f"Metadata keys: {list(metadata.keys())}")
            logger.info(f"Has basic_translation key: {'basic_translation' in metadata}")
            logger.info(f"Basic != Enhanced: {metadata.get('basic_translation') != translated}")

            # Show two-stage translation if GPT enhancement was performed (for premium users)
            if 'basic_translation' in metadata and has_premium:
                logger.info("Showing two-stage translation (basic + enhanced) for premium user")
                response_text += f"📝 *Точный перевод:*\n{metadata['basic_translation']}\n\n"
                response_text += f"✨ *Улучшенный перевод (GPT-4o):*\n{translated}"

                # Add synonyms/alternatives if available
                if metadata.get('alternatives'):
                    response_text += f"\n\n🔄 *Альтернативы:*\n"
                    for alt in metadata['alternatives'][:2]:  # Show max 2 alternatives
                        response_text += f"• {alt}\n"

                # Add explanation if available
                if metadata.get('explanation') and metadata['explanation'].strip():
                    explanation = metadata['explanation'].strip()[:200]  # Limit length
                    response_text += f"\n💡 *Объяснение:* {explanation}"
                    if len(metadata['explanation']) > 200:
                        response_text += "..."
            else:
                logger.info("Showing single translation (no two stages)")
                response_text += f"📝 *Перевод:*\n{translated}"

            # Add remaining translations info for free users
            if not user_info.get('is_premium'):
                response_text += f"\n\n📊 Осталось переводов сегодня: {remaining - 1}"

            # Add enhanced info for premium users
            if user_info.get('is_premium') and metadata.get('alternatives'):
                response_text += f"\n\n🔄 *Альтернативы:*\n"
                for alt in metadata['alternatives'][:2]:
                    response_text += f"• {alt}\n"

            keyboard = get_translation_actions_keyboard(True, user_info.get('is_premium', False))

            # Store metadata for callback buttons
            if user_info.get('is_premium', False):
                from bot.handlers.callbacks import last_translation_metadata
                logger.info(f"Storing metadata for user {message.from_user.id}: keys = {list(metadata.keys())}")
                logger.info(f"Alternatives: {metadata.get('alternatives', 'Not found')}")
                logger.info(f"Explanation: {metadata.get('explanation', 'Not found')}")
                logger.info(f"Grammar: {metadata.get('grammar', 'Not found')}")
                last_translation_metadata[message.from_user.id] = metadata

            logger.info(f"Sending response to user {message.from_user.id}")
            await message.answer(
                response_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.info("Response sent successfully")

            # Auto voice if enabled
            if user_info.get('auto_voice') and user_info.get('is_premium'):
                try:
                    async with VoiceService() as voice_service:
                        # Use basic translation for voice (more accurate pronunciation)
                        voice_text = metadata.get('basic_translation', translated)
                        logger.info(f"Generating voice for: {voice_text[:50]}...")
                        audio_data = await voice_service.generate_speech(
                            text=voice_text,
                            language=target_lang,
                            premium=True,
                            speed=user_info.get('voice_speed', 1.0)
                        )

                        if audio_data:
                            from aiogram.types import BufferedInputFile
                            audio_file = BufferedInputFile(audio_data, filename="translation.mp3")
                            await message.answer_voice(audio_file)
                except Exception as e:
                    logger.error(f"Auto voice error: {e}")

    except Exception as e:
        logger.error(f"Translation error: {e}")
        await message.answer(get_text('translation_failed', user_info.get('interface_language', 'ru')))