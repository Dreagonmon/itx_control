import hal_screen, hal_keypad
from ui.dialog import dialog
from ui.input_text import input_text
from ui.select import select_list, select_menu
from ui.progress import progress_gen
from aio import AsyncReader
from usys import stdin
import ujson

def main(app_name, *args, **kws):
    hal_screen.init()
    hal_keypad.init()
    print("================")
    server_task()

def server_task():
    # STX = "␂"
    # ETX = "␃"
    reader = AsyncReader(stdin)
    progress = progress_gen("", "Waiting...")
    read_gen = reader.readline_gen(True)
    while True:
        next(progress)
        for _ in range(512):
            inp = next(read_gen)
            if inp != None:
                break
        if inp == None:
            continue
        read_gen = reader.readline_gen(True) # ready for next loop
        try:
            try:
                req = ujson.loads(inp)
            except ValueError as e:
                if len(inp) > 0:
                    print(len(inp), inp)
                continue
            event = req["event"]
            if event == "protocol_version":
                # version is required
                print(ujson.dumps({
                    "event": "protocol_version_return",
                    "version": 1.0,
                }))
            elif event == "dialog":
                text = req["text"]
                title = req["title"]
                text_yes = req["text_yes"]
                text_no = req["text_no"]
                value = dialog(text, title, text_yes, text_no)
                print(ujson.dumps({
                    "event": "dialog_return",
                    "value": value,
                }))
            elif event == "select_menu":
                text = req["text"]
                title = req["title"]
                text_yes = req["text_yes"]
                text_no = req["text_no"]
                options = req["options"]
                value = select_menu(text, title, options, text_yes, text_no)
                print(ujson.dumps({
                    "event": "select_menu_return",
                    "value": value,
                }))
            elif event == "select_list":
                title = req["title"]
                text_yes = req["text_yes"]
                text_no = req["text_no"]
                options = req["options"]
                value = select_list(title, options, text_yes, text_no)
                print(ujson.dumps({
                    "event": "select_list_return",
                    "value": value,
                }))
            elif event == "input_text":
                text = req["text"]
                title = req["title"]
                value = input_text(text, title)
                print(ujson.dumps({
                    "event": "input_text_return",
                    "value": value,
                }))
        except Exception as e:
            import usys
            usys.print_exception(e)
