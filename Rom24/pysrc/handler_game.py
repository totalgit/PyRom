import handler_ch
import handler_obj
from merc import *
import interp
import state_checks
import game_utils
__author__ = 'venom'


class GEN_DATA:
    def __init__(self):
        self.valid = False
        self.skill_chosen = {}
        self.group_chosen = {}
        self.points_chosen = 0


class SOCIAL_DATA:
    def __init__(self):
        self.name = ""
        self.char_no_arg = ""
        self.others_no_arg = ""
        self.char_found = ""
        self.others_found = ""
        self.vict_found = ""
        self.char_not_found = ""
        self.char_auto = ""
        self.others_auto = ""


# An affect.
class AFFECT_DATA:
    def __init__(self):
        self.valid = True
        self.where = 0
        self.type = 0
        self.level = 0
        self.duration = 0
        self.location = 0
        self.modifier = 0
        self.bitvector = 0


class HELP_DATA:
    def __init__(self):
        self.level = 0
        self.keyword = ""
        self.text = ""

    def __repr__(self):
        return "<%s:%d>" % (self.keyword, self.level)


class time_info_data:
    def __init__(self):
        self.hour = 0
        self.day = 0
        self.month = 0
        self.year = 0


class weather_data:
    def __init__(self):
        self.mmhg = 0
        self.change = 0
        self.sky = 0
        self.sunlight = 0

time_info = time_info_data()
weather_info = weather_data()


def act(format, ch, arg1, arg2, send_to, min_pos = POS_RESTING):
    if not format:
        return
    if not ch or not ch.in_room:
        return

    vch = arg2
    obj1 = arg1
    obj2 = arg2

    he_she = ["it",  "he",  "she"]
    him_her = ["it",  "him", "her"]
    his_her = ["its", "his", "her"]

    to_players = ch.in_room.people

    if send_to is TO_VICT:
        if not vch:
            print ("Act: null vict with TO_VICT: " + format)
            return
        if not vch.in_room:
            return
        to_players = vch.in_room.people

    for to in to_players:
        if not to.desc or to.position < min_pos:
            continue
        if send_to is TO_CHAR and to is not ch:
            continue
        if send_to is TO_VICT and ( to is not vch or to is ch ):
            continue
        if send_to is TO_ROOM and to is ch:
            continue
        if send_to is TO_NOTVICT and (to is ch or to is vch):
            continue

        act_trans = {}
        if arg1:
            act_trans['$t'] = str(arg1)
        if arg2 and type(arg2) == str:
            act_trans['$T'] = str(arg2)
        if ch:
            act_trans['$n'] = state_checks.PERS(ch, to)
            act_trans['$e'] = he_she[ch.sex]
            act_trans['$m'] = him_her[ch.sex]
            act_trans['$s'] = his_her[ch.sex]
        if vch and type(vch) == handler_ch.CHAR_DATA:
            act_trans['$N'] = state_checks.PERS(vch, to)
            act_trans['$E'] = he_she[vch.sex]
            act_trans['$M'] = him_her[vch.sex]
            act_trans['$S'] = his_her[vch.sex]
        if obj1 and obj1.__class__ == handler_obj.OBJ_DATA:
            act_trans['$p'] = state_checks.OPERS(to, obj1)
        if obj2 and obj2.__class__ == handler_obj.OBJ_DATA:
            act_trans['$P'] = state_checks.OPERS(to, obj2)
        act_trans['$d'] = arg2 if not arg2 else "door"

        format = game_utils.mass_replace(format, act_trans)
        to.send(format+"\n")
    return


def wiznet( string, ch, obj, flag, flag_skip, min_level):
    from nanny import con_playing
    for d in descriptor_list:
        if   d.is_connected(con_playing) \
        and  state_checks.IS_IMMORTAL(d.character) \
        and  state_checks.IS_SET(d.character.wiznet, WIZ_ON) \
        and  (not flag or state_checks.IS_SET(d.character.wiznet,flag)) \
        and  (not flag_skip or not state_checks.IS_SET(d.character.wiznet,flag_skip)) \
        and  d.character.get_trust() >= min_level \
        and  d.character != ch:
            if state_checks.IS_SET(d.character.wiznet,WIZ_PREFIX):
                d.send("-. ",d.character)
            act(string,d.character,obj,ch,TO_CHAR,POS_DEAD)


# does aliasing and other fun stuff */
def substitute_alias(d, argument):
    ch = handler_ch.CH(d)
    MAX_INPUT_LENGTH = 500
    # check for prefix */
    if ch.prefix and not "prefix".startswith(argument):
        if len(ch.prefix) + len(argument) > MAX_INPUT_LENGTH:
            ch.send("Line to long, prefix not processed.\r\n")
        else:
            prefix = "%s %s" % (ch.prefix,argument)

    if state_checks.IS_NPC(ch) or not ch.pcdata.alias \
    or "alias".startswith(argument) or "unalias".startswith(argument)  \
    or "prefix".startswith(argument):
        interp.interpret(ch,argument)
        return
    remains, sub = game_utils.read_word(argument)
    if sub not in ch.pcdata.alias:
        interp.interpret(ch, argument)
        return
    buf = "%s %s" % ( ch.pcdata.alias[sub], remains )
    interp.interpret(ch,buf)