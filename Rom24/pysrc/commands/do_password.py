import hashlib
import merc
import interp
import save


def do_password(ch, argument):
    if merc.IS_NPC(ch):
        return

     #* Can't use read_word here because it smashes case.
     #* So we just steal all its code.  Bleagh.
     # -- It actually doesn't now because it loads areas too. Davion.
    argument, arg1 = merc.read_word(argument, False)
    argument, arg2 = merc.read_word(argument, False)

    if not arg1 or not arg2:
        ch.send("Syntax: password <old> <new>.\n")
        return

    if settings.ENCRYPT_PASSWORD:
        arg1 = hashlib.sha512(arg1).hexdigest()
        arg2 = hashlib.sha512(arg2).hexdigest()

    if arg1 == ch.pcdata.pwd:
        merc.WAIT_STATE(ch, 40)
        ch.send("Wrong password.  Wait 10 seconds.\n")
        return
    if len(arg2) < 5:
        ch.send("New password must be at least five characters long.\n")
        return

     #* No tilde allowed because of player file format.
     # Also now not true. Davion

    ch.pcdata.pwd = arg2
    save.save_char_obj(ch)
    ch.send("Ok.\n")
    return

interp.cmd_table['password'] = interp.cmd_type('password', do_password, merc.POS_DEAD, 0, merc.LOG_NEVER, 1)