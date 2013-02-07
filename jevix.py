#coding: utf-8

import htmlentitydefs
import re
import cgi
import sys

class Jevix:

    PRINATABLE  = 0x1;
    ALPHA       = 0x2;
    LAT         = 0x4;
    RUS         = 0x8;
    NUMERIC     = 0x10;
    SPACE       = 0x20;
    NAME        = 0x40;
    URL         = 0x100;
    NOPRINT     = 0x200;
    PUNCTUATUON = 0x400;
    #          = 0x800;
    #          = 0x1000;
    HTML_QUOTE  = 0x2000;
    TAG_QUOTE   = 0x4000;
    QUOTE_CLOSE = 0x8000;
    NL          = 0x10000;
    QUOTE_OPEN  = 0;

    STATE_TEXT = 0;
    STATE_TAG_PARAMS = 1;
    STATE_TAG_PARAM_VALUE = 2;
    STATE_INSIDE_TAG = 3;
    STATE_INSIDE_NOTEXT_TAG = 4;
    STATE_INSIDE_PREFORMATTED_TAG = 5;
    STATE_INSIDE_CALLBACK_TAG = 6;

    tagsRules = {}
    entities0 = {u'"':u'&quot;', u"'":u'&#39;', u'&':u'&amp;', u'<':u'&lt;', u'>':u'&gt;'}
    entities1 = {}
    entities2 = {u'<':u'&lt;', u'>':u'&gt;', u'"':u'&quot;'}
    textQuotes = [[u'«', u'»'], [u'„', u'“']]
    dashText = u" — ";
    apostrof = u"’";
    dotes = u"…";
    nl = u"\r\n";
    defaultTagParamRules = {u'href' : u'#link', u'src' : u'#image', u'width' : u'#int', u'height' : u'#int', u'text' : u'#text', u'title' : u'#text'}

    text = '';
    textBuf = {};
    textLen = 0;
    curPos = -1;
    curCh = '';
    curChOrd = 0;
    curChClass = 0;
    curParentTag = {}
    states = {};
    quotesOpened = 0;
    brAdded = 0;
    state = 0;
    tagsStack = [];
    openedTag = '';
    autoReplace = {}; # Автозамена
    linkProtocolAllow = []
    linkProtocolAllowDefault = [u'http',u'https',u'ftp']
    isXHTMLMode  = True; # <br/>, <img/>
    isAutoBrMode = True; # \n = <br/>
    isAutoLinkMode = True;
    br = u"<br/>";

    noTypoMode = False;

    outBuffer = u'';
    errors = [];


    
    # Константы для класификации тегов
    TR_TAG_ALLOWED = 1; 		 # Тег позволен
    TR_PARAM_ALLOWED = 2; 	 # Параметр тега позволен (a->title, a->src, i->alt)
    TR_PARAM_REQUIRED = 3; 	 # Параметр тега влятся необходимым (a->href, img->src)
    TR_TAG_SHORT = 4;   		 # Тег может быть коротким (img, br)
    TR_TAG_CUT = 5;			 # Тег необходимо вырезать вместе с контентом (script, iframe)
    TR_TAG_CHILD = 6;			 # Тег может содержать другие теги
    TR_TAG_CONTAINER = 7;      # Тег может содержать лишь указанные теги. В нём не может быть текста
    TR_TAG_CHILD_TAGS = 8;	 # Теги которые может содержать внутри себя другой тег
    TR_TAG_PARENT = 9;		 # Тег в котором должен содержаться данный тег
    TR_TAG_PREFORMATTED = 10;	 # Преформатированные тег, в котором всё заменяется на HTML сущности типа <pre> сохраняя все отступы и пробелы
    TR_PARAM_AUTO_ADD = 11;    # Auto add parameters + default values (a->rel[=nofollow])
    TR_TAG_NO_TYPOGRAPHY = 12; # Отключение типографирования для тега

    TR_TAG_IS_EMPTY = 13;      # Не короткий тег с пустым содержанием имеет право существовать
    TR_TAG_NO_AUTO_BR = 14;    # Тег в котором не нужна авто-расстановка <br>
    TR_TAG_CALLBACK = 15;      # Тег обрабатывается callback-функцией - в обработку уходит только контент тега(короткие теги не обрабатываются)
    TR_TAG_BLOCK_TYPE = 16;    # Тег после которого не нужна автоподстановка доп. <br>
    TR_TAG_CALLBACK_FULL = 17; # Тег обрабатывается callback-функцией - в обработку уходит весь тег


# Классы символов генерируются symclass.php
    chClasses = {0:512,1:512,2:512,3:512,4:512,5:512,6:512,7:512,8:512,9:32,10:66048,11:512,12:512,13:66048,14:512,15:512,16:512,17:512,18:512,19:512,20:512,21:512,22:512,23:512,24:512,25:512,26:512,27:512,28:512,29:512,30:512,31:512,32:32,97:71,98:71,99:71,100:71,101:71,102:71,103:71,104:71,105:71,106:71,107:71,108:71,109:71,110:71,111:71,112:71,113:71,114:71,115:71,116:71,117:71,118:71,119:71,120:71,121:71,122:71,65:71,66:71,67:71,68:71,69:71,70:71,71:71,72:71,73:71,74:71,75:71,76:71,77:71,78:71,79:71,80:71,81:71,82:71,83:71,84:71,85:71,86:71,87:71,88:71,89:71,90:71,1072:11,1073:11,1074:11,1075:11,1076:11,1077:11,1078:11,1079:11,1080:11,1081:11,1082:11,1083:11,1084:11,1085:11,1086:11,1087:11,1088:11,1089:11,1090:11,1091:11,1092:11,1093:11,1094:11,1095:11,1096:11,1097:11,1098:11,1099:11,1100:11,1101:11,1102:11,1103:11,1040:11,1041:11,1042:11,1043:11,1044:11,1045:11,1046:11,1047:11,1048:11,1049:11,1050:11,1051:11,1052:11,1053:11,1054:11,1055:11,1056:11,1057:11,1058:11,1059:11,1060:11,1061:11,1062:11,1063:11,1064:11,1065:11,1066:11,1067:11,1068:11,1069:11,1070:11,1071:11,48:337,49:337,50:337,51:337,52:337,53:337,54:337,55:337,56:337,57:337,34:57345,39:16385,46:1281,44:1025,33:1025,63:1281,58:1025,59:1281,1105:11,1025:11,47:257,38:257,37:257,45:257,95:257,61:257,43:257,35:257,124:257}


    def _cfgSetTagsFlag (self,tags, flag, value, createIfNoExists = True):
        """
            Установка конфигурационного флага для одного или нескольких тегов
        """

        for tag in tags:
            if not self.tagsRules.has_key(tag):
                if createIfNoExists:
                    self.tagsRules[tag] = {}
                else:
                    # Тег tag отсутствует в списке разрешённых тегов
                    raise Exception(u"Тег %s отсутствует в списке разрешённых тегов" % tag)

            self.tagsRules[tag][flag] = value


    def cfgAllowTags (self, tags):
        """
            КОНФИГУРАЦИЯ: Разрешение или запрет тегов
	        Все не разрешённые теги считаются запрещёнными
        """
        self._cfgSetTagsFlag(tags, self.TR_TAG_ALLOWED, True)


    def cfgSetTagShort (self, tags):
        """
            КОНФИГУРАЦИЯ: Коротие теги типа <img>
        """
        self._cfgSetTagsFlag(tags, self.TR_TAG_SHORT, True, False)

    def cfgSetTagPreformatted (self, tags):
       """
        КОНФИГУРАЦИЯ: Преформатированные теги, в которых всё заменяется на HTML сущности типа <pre>
       """
       self._cfgSetTagsFlag(tags, self.TR_TAG_PREFORMATTED, True, False)

    def cfgSetTagNoTypography (self, tags):
       """
        КОНФИГУРАЦИЯ: Теги в которых отключено типографирование типа <code>
       """
       self._cfgSetTagsFlag(tags, self.TR_TAG_NO_TYPOGRAPHY, True, False)

    def cfgSetTagCutWithContent (self, tags):
       """
        КОНФИГУРАЦИЯ: Тег необходимо вырезать вместе с контентом (script, iframe)
       """
       self._cfgSetTagsFlag(tags, self.TR_TAG_CUT, True)


    def cfgAllowTagParams(self, tag, params):
        """
            КОНФИГУРАЦИЯ: Добавление разрешённых параметров тега
        """

        if not self.tagsRules.has_key(tag):
            raise Exception(u"Тег %s отсутствует в списке разрешённых тегов" % tag)

        #Если ключа со списком разрешенных параметров не существует - создаём его
        if not self.tagsRules[tag].has_key(self.TR_PARAM_ALLOWED):
            self.tagsRules[tag][self.TR_PARAM_ALLOWED] = {}

        for key, value in params.items():
            if type(key) is str:
                self.tagsRules[tag][self.TR_PARAM_ALLOWED][key] = value
            else:
                self.tagsRules[tag][self.TR_PARAM_ALLOWED][value] = True


    def cfgSetTagParamsRequired(self, tag, params):
        """
            КОНФИГУРАЦИЯ: Добавление необходимых параметров тега
        """

        if not self.tagsRules.has_key(tag):
            raise Exception(u"Тег %s отсутствует в списке разрешённых тегов" % tag)

        #Если ключа со списком разрешенных параметров не существует - создаём его
        if not self.tagsRules[tag].has_key(self.TR_PARAM_REQUIRED):
            self.tagsRules[tag][self.TR_PARAM_REQUIRED] = {}

        for param in params:
            self.tagsRules[tag][self.TR_PARAM_REQUIRED][param] = True


    def cfgSetTagIsEmpty(self, tags):
        self._cfgSetTagsFlag(tags, self.TR_TAG_IS_EMPTY, True, False)

    def cfgSetTagNoAutoBr(self, tags):
        self._cfgSetTagsFlag(tags, self.TR_TAG_NO_AUTO_BR, True, False)

    def cfgSetTagBlockType(self, tags):
        self._cfgSetTagsFlag(tags, self.TR_TAG_BLOCK_TYPE, True)


    def cfgSetTagChilds(self, tag, childs, isContainerOnly = False, isChildOnly = False):
        """
            КОНФИГУРАЦИЯ: Установка тегов которые может содержать тег-контейнер
        """

        if not self.tagsRules.has_key(tag):
            raise Exception(u"Тег %s отсутствует в списке разрешённых тегов" % tag)

        # Тег является контейнером и не может содержать текст
        if isContainerOnly:
            self.tagsRules[tag][self.TR_TAG_CONTAINER] = True

        #Если ключа со списком разрешенных тегов не существует - создаём его
        if not self.tagsRules[tag].has_key(self.TR_TAG_CHILD_TAGS):
            self.tagsRules[tag][self.TR_TAG_CHILD_TAGS] = {}

        for child in childs:
            self.tagsRules[tag][self.TR_TAG_CHILD_TAGS][child] = True
            #  Указанный тег должен сущеаствовать в списке тегов
            if not self.tagsRules.has_key(child):
                raise Exception(u"Тег %s отсутствует в списке разрешённых тегов" % child)

            if not self.tagsRules[child].has_key(self.TR_TAG_PARENT):
                self.tagsRules[child][self.TR_TAG_PARENT] = {}

            self.tagsRules[child][self.TR_TAG_PARENT][tag] = True

            # Указанные разрешённые теги могут находится только внтутри тега-контейнера
            if isChildOnly:
                self.tagsRules[child][self.TR_TAG_CHILD] = True


    def cfgSetTagParamsAutoAdd(self, tag, params):
        """
            CONFIGURATION: Adding autoadd attributes and their values to tag
        """

        if not self.tagsRules.has_key(tag):
            raise Exception(u"Тег %s отсутствует в списке разрешённых тегов" % tag)

        #Если ключа со списком разрешенных параметров не существует - создаём его
        if not self.tagsRules[tag].has_key(self.TR_PARAM_AUTO_ADD):
            self.tagsRules[tag][self.TR_PARAM_AUTO_ADD] = {}

        for param in params.values():
            self.tagsRules[tag][self.TR_PARAM_AUTO_ADD][param] = True



    def cfgSetAutoReplace(self, froms, to):
        """
            Автозамена
        """

        self.autoReplace = {"from" : froms, "to" : to}


    def cfgSetXHTMLMode(self, isXHTMLMode):
        """
            Включение или выключение режима XTML
        """

        self.br = '<br/>' if isXHTMLMode else '<br>'
        self.isXHTMLMode = isXHTMLMode


    def cfgSetAutoBrMode(self, isAutoBrMode):
        """
            Включение или выключение режима замены новых строк на <br/>
        """

        self.isAutoBrMode = isAutoBrMode


    def cfgSetAutoLinkMode(self, isAutoLinkMode):
        """
            Включение или выключение режима автоматического определения ссылок
        """

        self.isAutoLinkMode = isAutoLinkMode


    def strToArray(self, strs):
        chars = re.findall('(?su).', strs)
        return chars

    def multiple_replace(dic, text):
        pattern = u"|".join(map(re.escape, dic.keys()))
        return re.sub(pattern, lambda m: dic[m.group()], text)



    def parse(self, text, errors = []):

        self.curPos = -1
        self.curCh = ''
        self.curChOrd = 0
        self.state = self.STATE_TEXT
        self.states = {}
        self.quotesOpened = 0
        self.noTypoMode = False

        #Авто растановка BR?
        if self.isAutoBrMode:
            self.text = re.sub(u'(?ui)<br/?>(\r\n|\n\r|\n)?', self.nl, text)
        else:
            self.text = text



        if len(self.autoReplace) > 0:
            self.text = self.multiple_replace(self.autoReplace, self.text)


        self.textBuf = self.strToArray(self.text)
        self.textLen = len(self.textBuf)
        self.getCh()
        content = u''
        self.outBuffer = u''
        self.brAdded = 0
        self.tagsStack = []
        self.openedTag = u''
        self.errors = []
        self.skipSpaces()
        content,bool_content = self.anyThing(content)
        errors = self.errors

        return  content, errors


    def getCh(self):
        return self.goToPosition(self.curPos+1)

    def goToPosition(self, position):
        """
        Перемещение на указанную позицию во входной строке и считывание символа
        """
        self.curPos = position

        if self.curPos < self.textLen:
            self.curCh = self.textBuf[self.curPos]
            self.curChOrd = ord(self.curCh)
            self.curChClass = self.getCharClass(self.curChOrd)
        else:
            self.curCh = ''
            self.curChOrd = 0
            self.curChClass = 0

        return self.curCh


    def saveState(self):
        """
        Сохранить текущее состояние
        """

        states = {
            'pos'   : self.curPos,
            'ch'    : self.curCh,
            'ord'   : self.curChOrd,
            'class' : self.curChClass,
        }


        self.states[len(self.states)] = states

        return len(self.states)-1


    def restoreState(self, index = -1):
        """
            Восстановить
        """
        if not len(self.states):
            raise Exception(u'Конец стека');

        if index == -1:
            state = self.states[list(self.states.keys()).pop()]
            del self.states[list(self.states.keys()).pop()]
        else:
            if not self.states.has_key(index):
                raise Exception(u'Неверный индекс стека');
            state = self.states[index]
            keys = list(self.states.keys())[0:index]
            old = self.states.copy()
            self.states.clear()
            for key in keys:
                self.states[key] = old[key]

        self.curPos = state['pos']
        self.curCh = state['ch']
        self.curChOrd = state['ord']
        self.curChClass = state['class']



    def matchCh(self, ch, skipSpaces = False):
        """
            Проверяет точное вхождение символа в текущей позиции
	        Если символ соответствует указанному автомат сдвигается на следующий
        """

        if self.curCh == ch:
            self.getCh()
            if skipSpaces:
                self.skipSpaces()
            return True

        return False


    def matchChClass(self, chClass, skipSpaces = False):
        """
            Проверяет точное вхождение символа указанного класса в текущей позиции
	        Если символ соответствует указанному классу автомат сдвигается на следующий
        """

        if (self.curChClass & chClass) == chClass:
            ch = self.curCh
            self.getCh()
            if skipSpaces:
                self.skipSpaces()
            return ch

        return False


    def matchStr(self, strs, skipSpaces = False):
        """
            Проверка на точное совпадение строки в текущей позиции
	        Если строка соответствует указанной автомат сдвигается на следующий после строки символ
        """

        self.saveState()
        lens = len(strs)
        test = u''
        while lens > 0 and self.curChClass:
            test += self.curCh
            self.getCh()
            lens -= 1

        if test == strs:
            if skipSpaces:
                self.skipSpaces()
            return True
        else:
            self.restoreState()
            return False


    def skipUntilCh(self, ch):
        """
        Пропуск текста до нахождения указанного символа
        """

        chPos = self.text.find(ch, self.curPos)
        if chPos:
            return self.goToPosition(chPos)
        else:
            return False



    def skipUntilStr(self, strs):
        """
        Пропуск текста до нахождения указанной строки или символа
        """

        strs = self.strToArray(strs)
        firstCh = strs[0]
        lens = len(strs)

        while self.curChClass:

            if self.curCh == firstCh:
                self.saveState()
                self.getCh()
                strOK = True
                i = 1
                while i < lens:
                    #Конец строки
                    if self.curChClass:
                        return False
                    #текущий символ не равен текущему символу проверяемой строки?
                    if self.curCh != strs[i]:
                        strOK = False
                        break
                    # Следующий символ
                    self.getCh()
                    i += 1

                #При неудаче откатываемся с переходим на следующий символ
                if strOK:
                    self.restoreState()
                else:
                    return True

            self.getCh()

        return False


    def getCharClass(self, ords):
        """
            Возвращает класс символа
        """
        return self.chClasses[ords] if self.chClasses.has_key(ords) else self.PRINATABLE


    def name(self, name = u'', minus = False):
        """
            Получает име (тега, параметра) по принципу 1 сиивол далее цифра или символ
        """

        name = str(name)

        if (self.curChClass & self.LAT) == self.LAT:
            name += self.curCh
            self.getCh()
        else:
            return name,False

        while (self.curChClass & self.NAME) == self.NAME or (minus and self.curCh=='-'):
            name += self.curCh
            self.getCh()

        self.skipSpaces()

        return name,True

    def tag(self, tag, params, content, short):
        self.saveState()
        params = {}
        tag = u''
        closeTag = u''
        short = False

        tag, params, short, bool_tag = self.tagOpen(tag, params, short)
        if not bool_tag:
            return tag, params, content, short,False

        # Короткая запись тега
        if short:
            return tag, params, content, short,True

        oldState = self.state
        oldNoTypoMode = self.noTypoMode

        #Если в теге не должно быть текста, а только другие теги
        #Переходим в состояние self.STATE_INSIDE_NOTEXT_TAG

        if self.tagsRules.has_key(tag) and self.tagsRules[tag].has_key(self.TR_TAG_PREFORMATTED):
            self.state = self.STATE_INSIDE_PREFORMATTED_TAG
        elif self.tagsRules.has_key(tag) and self.tagsRules[tag].has_key(self.TR_TAG_CONTAINER):
            self.state = self.STATE_INSIDE_NOTEXT_TAG
        elif self.tagsRules.has_key(tag) and self.tagsRules[tag].has_key(self.TR_TAG_NO_TYPOGRAPHY):
            self.noTypoMode = True
            self.state = self.STATE_INSIDE_TAG
        elif self.tagsRules.has_key(tag) and self.tagsRules[tag].has_key(self.TR_TAG_CALLBACK):
            self.state = self.STATE_INSIDE_CALLBACK_TAG
        else:
            self.state = self.STATE_INSIDE_TAG

        #Контент тега
        self.tagsStack.append(tag)
        self.openedTag = tag
        content = ''

        if self.state == self.STATE_INSIDE_PREFORMATTED_TAG:
            content = self.preformatted(content, tag)
        elif self.state == self.STATE_INSIDE_CALLBACK_TAG:
            content = self.callback(content, tag)
        else:
            content,bool_content = self.anyThing(content, tag)

        if len(self.tagsStack) > 0:
            self.tagsStack.pop()
            self.openedTag = self.tagsStack.pop() if len(self.tagsStack) > 0 else None
        else:
            self.openedTag = None

        closeTag, isTagClose = self.tagClose(closeTag)

        if isTagClose and (tag != closeTag):
            self.eror(u'Неверный закрывающийся тег %s. Ожидалось закрытие %s' % (closeTag, tag))


        #Восстанавливаем предыдущее состояние и счетчик кавычек
        self.state = oldState
        self.noTypoMode = oldNoTypoMode

        return tag, params, content, short,True


    def preformatted(self, content = '', insideTag = ''):
        while self.curChClass:
            if self.curCh == '<':
                tag = ''
                self.saveState()
                #Пытаемся найти закрывающийся тег
                tag, isClosedTag = self.tagClose(tag)
                #Возвращаемся назад, если тег был найден
                if isClosedTag:
                    self.restoreState()
                #Если закрылось то, что открылось - заканчиваем и возвращаем True
                if isClosedTag and tag == insideTag:
                    return content

            content += self.entities2[self.curCh] if self.entities2.has_key(self.curCh) else self.curCh
            self.getCh()
        return content


    def callback(self, content, insideTag = ''):
        while self.curChClass:
            if self.curCh == '<':
                tag = ''
                self.saveState()
                #Пытаемся найти закрывающийся тег
                tag, isClosedTag = self.tagClose(tag)
                #Возвращаемся назад, если тег был найден
                if isClosedTag:
                    self.restoreState()
                #Если закрылось то, что открылось - заканчиваем и возвращаем True
                if isClosedTag and tag == insideTag:
                    callback = self.tagsRules[tag][self.TR_TAG_CALLBACK]
                    content = locals()[callback](content)
                    return content
            content += self.curCh
            self.getCh()
        return content


    def tagOpen(self, name, params, short = False):
        restore = self.saveState()

        #Открытие
        if not self.matchCh(u'<'):
            return name, params, short,False
        self.skipSpaces()
        name, bool_name = self.name(name)

        if not bool_name:
            self.restoreState()
            return name, params, short,False

        name = name.lower()

        #Пробуем получить список атрибутов тега

        if self.curCh != u'>' and self.curCh != u'/':
            params, bool_tagParams = self.tagParams(params)

        #Короткая запись тега
        short = self.tagsRules.has_key(name) and self.tagsRules[name].has_key(self.TR_TAG_SHORT)

        #Short and XHTML and !Slash or Short and !XHTML and !Slash = ERROR
        slash = self.matchCh(u'/');

        if short and slash:
            self.restoreState()
            return name, params, short,False


        self.skipSpaces()

        #Закрытие
        if not self.matchCh(u'>'):
            self.restoreState(restore)
            return name, params, short,False

        self.skipSpaces()
        return name, params, short,True



    def tagParams(self, params = {}):
        name = ''
        value = ''
        name, value, bool_tag = self.tagParam(name, value)
        while bool_tag:
            params[name] = value
            name = ''
            value = ''
            name, value, bool_tag = self.tagParam(name, value)

        return params, (len(params)>0)


    def tagParam(self, name, value):
        self.saveState()
        name, bool_name = self.name(name, True)
        if not bool_name:
            return name,value,False

        if not self.matchCh('=', True):
            #Стремная штука - параметр без значения <input type="checkbox" checked>, <td nowrap class=b>
            if self.curCh=='>' or (self.curChClass & self.LAT) == self.LAT:
                value = name
                return name,value,True
            else:
                self.restoreState()
                return name,value,False



        quote = self.matchChClass(self.TAG_QUOTE, True)

        value, bool_tag = self.tagParamValue(value, quote)
        if not bool_tag:
            self.restoreState()
            return name,value,False

        if quote and not self.matchCh(quote, True):
            self.restoreState()
            return name,value,False

        self.skipSpaces()
        return name,value,True


    def tagParamValue(self, value, quote):
        if quote != False:
            escape = False
            while self.curChClass and (self.curCh != quote or escape):
                escape = False
                #Экранируем символы HTML которые не могут быть в параметрах
                value += self.entities1[self.curCh] if self.entities1.has_key(self.curCh) else self.curCh
                if self.curCh == '\\':
                    escape = True
                self.getCh()
        else:
            while self.curChClass and not (self.curChClass & self.SPACE) and self.curCh != '>':
                #Экранируем символы HTML которые не могут быть в параметрах
                value += self.entities1[self.curCh] if self.entities1.has_key(self.curCh) else self.curCh
                self.getCh()

        return value,True


    def tagClose(self, name):
        self.saveState()
        if not self.matchCh(u'<'):
            return name,False
        self.skipSpaces();
        if not self.matchCh(u'/'):
            self.restoreState();
            return name,False;

        self.skipSpaces();
        name, bool_name = self.name(name)
        if not bool_name:
            self.restoreState();
            return name,False;

        name = name.lower()
        self.skipSpaces();
        if not self.matchCh(u'>'):
            self.restoreState();
            return name,False;

        return name,True;


    def isset(variable):
        return variable in locals() or variable in globals()

    def makeTag(self, tag, params, content, short, parentTag = None):
        self.curParentTag=parentTag;
        tag = tag.lower()

        # Получаем правила фильтрации тега
        tagRules = self.tagsRules[tag] if self.tagsRules.has_key(tag) else None;

        # Проверка - родительский тег - контейнер, содержащий только другие теги (ul, table, etc)
        parentTagIsContainer = parentTag and self.tagsRules.has_key(parentTag) and self.tagsRules[parentTag].has_key(self.TR_TAG_CONTAINER);

        # Вырезать тег вместе с содержанием
        if tagRules and self.tagsRules.has_key(parentTag) and self.tagsRules[parentTag].has_key(self.TR_TAG_CUT):
            return '';

        # Позволен ли тег
        if not tagRules or (tagRules is dict and len(tagRules[self.TR_TAG_ALLOWED]) == 0):
            return u'' if parentTagIsContainer else content

        # Если тег находится внутри другого - может ли он там находится?
        if parentTagIsContainer:
            if not self.tagsRules.has_key(parentTag) and \
               self.tagsRules[parentTag].has_key(self.TR_TAG_CHILD_TAGS) \
                and self.tagsRules[parentTag][self.TR_TAG_CHILD_TAGS].has_key(tag):
                return u'';


        # Тег может находится только внтури другого тега
        if tagRules.has_key(self.TR_TAG_CHILD):
            if not tagRules[self.TR_TAG_PARENT].has_key(parentTag):
                return content;



        resParams = {}
        for param, value in params.items():
            param = param.lower()
            value = value.strip(u' ')

            if value == u'':
                continue


            if not tagRules[self.TR_PARAM_ALLOWED].has_key(param):
                paramAllowedValues = False
            else:
                paramAllowedValues = tagRules[self.TR_PARAM_ALLOWED][param]


            if not(paramAllowedValues or type(paramAllowedValues) is dict or type(paramAllowedValues) is list):
                continue

            if type(paramAllowedValues) is dict or type(paramAllowedValues) is list:
                if type(paramAllowedValues) is dict and \
                        paramAllowedValues.has_key(u'#domain') and \
                        type(paramAllowedValues[u'#domain']) is list:

                    if re.search(u'(?ui)javascript:', value):
                        self.eror(u'Попытка вставить JavaScript в URI')
                        continue;

                    bOK = False

                    for sDomain in paramAllowedValues[u'#domain']:
                        sDomain=re.escape(sDomain)
                        if re.search(u"(?ui)^(http|https|ftp)://([\w\d]+\.)?%s" % sDomain,value):
                            bOK = True
                            break

                    if not bOK:
                        self.eror(u"Недопустимое значение для атрибута тега %s %s=%s" % (tag, param, value))
                        continue
                elif type(paramAllowedValues) is list and not value in paramAllowedValues:
                    self.eror(u"Недопустимое значение для атрибута тега %s %s=%s" % (tag, param, value))
                    continue
                elif type(paramAllowedValues) is dict and not value in paramAllowedValues.values():
                    self.eror(u"Недопустимое значение для атрибута тега %s %s=%s" % (tag, param, value))
                    continue


            elif paramAllowedValues and self.defaultTagParamRules.has_key(param):
                paramAllowedValues = self.defaultTagParamRules[param]



            if type(paramAllowedValues) is str or type(paramAllowedValues) is unicode:

                if paramAllowedValues == u'#int':
                    if not re.search(r'(?ui)[\d]+', value):
                        self.eror(u"Недопустимое значение для атрибута тега %s %s=%s. Ожидалось число" % (tag, param, value));
                        continue
                elif paramAllowedValues == u'#text':
                    value = cgi.escape(value, True)
                elif paramAllowedValues == u'#link':
                    if re.search(u'(?ui)javascript:', value):
                        self.eror(u'Попытка вставить JavaScript в URI')
                        continue

                    if not re.search(u'(?ui)^[a-z0-9\/\#]', value):
                        self.eror(u'URI: Первый символ адреса должен быть буквой или цифрой');
                        continue

                    #HTTP в начале если нет
                    sProtocols = u"|".join(self.linkProtocolAllow if self.linkProtocolAllow else self.linkProtocolAllowDefault)
                    if not re.search(u'(?ui)^(%s):\/\/' % sProtocols, value) and not re.search('(?ui)^(\/|\#)', value) and not re.search('(?ui)^(mailto):', value):
                        value = u'http://' + value


                elif paramAllowedValues == u'#image':
                    if re.search('javascript:', value):
                        self.eror(u'Попытка вставить JavaScript в URI')

                    if not re.search(u'(?ui)^(http|https):\/\/', value) and not re.search('(?ui)^\/', value):
                        value = u'http://' + value

                else:
                    self.eror(u"Неверное описание атрибута тега в настройке Jevix: %s=%s. " % (param, paramAllowedValues));
                    continue;


            resParams[param] = value

        #Проверка обязятельных параметров тега
        requiredParams = tagRules[self.TR_PARAM_REQUIRED] if tagRules.has_key(self.TR_PARAM_REQUIRED) else False

        if requiredParams:
            for requiredParam in requiredParams.keys():
                if not resParams.has_key(requiredParam):
                    return content



        if tagRules.has_key(self.TR_PARAM_AUTO_ADD) and len(tagRules[self.TR_PARAM_AUTO_ADD]) > 0:
            for name, aValue in tagRules[self.TR_PARAM_AUTO_ADD]:
                if not resParams.has_key(name) or (aValue[u'rewrite'] and resParams[name] != aValue[u'value']):
                    resParams[name] = aValue[u'value']


        if not tagRules.has_key(self.TR_TAG_IS_EMPTY) or not tagRules[self.TR_TAG_IS_EMPTY]:
            if not short and content == '':
                return ''


        #Если тег обрабатывает "полным" колбеком
        if tagRules.has_key(self.TR_TAG_CALLBACK_FULL):
            text = locals()[tagRules[self.TR_TAG_CALLBACK_FULL]](tag, resParams, content)
        else:
            text=u'<' + tag

            #Параметры
            for param, value in resParams.items():
                if value != u'':
                    text += u' ' + param + u'="' + value + u'"'


            text += u'/>' if short and self.isXHTMLMode else u'>'
            if tagRules.has_key(self.TR_TAG_CONTAINER):
                text += u"\r\n"

            if not short:
                text += content + u"</" + tag + u'>'

            if parentTagIsContainer:
                text += u"\r\n"
            if tag ==u'br':
                text += u'\r\n'

        return text


    def comment(self):

        if not self.matchStr(u'<!--'):
            return False
        return  self.skipUntilStr(u'-->')

    def anyThing(self, content, parentTag = u''):
        self.skipNL()
        while self.curChClass:
            tag = u''
            params = None;
            text = None;
            shortTag = False;
            name = None;

            if self.state == self.STATE_INSIDE_NOTEXT_TAG and self.curCh!=u'<':
                self.skipUntilCh(u'<')

            bool_tag = False
            if (self.curCh == u'<'):
                tag, params, text, shortTag, bool_tag = self.tag(tag, params, text, shortTag)

            if bool_tag:
                tagText = self.makeTag(tag, params, text, shortTag, parentTag)
                if tagText:
                    content += tagText

                if tag == u'br':
                    self.skipNL()
                elif self.tagsRules.has_key(tag) and self.tagsRules[tag].has_key(self.TR_TAG_BLOCK_TYPE):
                    count = 0
                    count, bool_count = self.skipNL(count, 2)
                elif tagText==u'':
                    self.skipSpaces()
                continue


            if self.curCh == u'<' and self.comment():
                continue

            if self.curCh == u'<':
                self.saveState()
                name, bool_name = self.tagClose(name)
                if bool_name:
                    if self.state == self.STATE_INSIDE_TAG or self.state == self.STATE_INSIDE_NOTEXT_TAG:
                        self.restoreState()
                        return content,False
                    else:
                        self.eror(u'Не ожидалось закрывающегося тега %s' % name);
                else:
                    if self.state != self.STATE_INSIDE_NOTEXT_TAG:
                        content += self.entities2[u'<']
                    self.getCh()
                continue

            text, boolText = self.textFunction(text)
            if boolText:
                content += text




        return content,True


    def skipNL(self, count=0, limit=0):
        if not self.curChClass & self.NL:
            return count,False
        count += 1
        firstNL = self.curCh
        nl = self.getCh()

        while self.curChClass & self.NL:

            if limit>0 and count >= limit:
                break

            if nl == firstNL:
                count += 1
            nl = self.getCh()

            self.skipSpaces()

        return count,True



    def dash(self, dashText):
        if self.curCh != '-':
            return dashText,False
        dashText = ''
        self.saveState()
        self.getCh()

        while self.curCh == '-':
            self.getCh()

        co, bool_nl = self.skipNL()
        spCount, bool_spCount = self.skipSpaces()
        if not bool_nl and bool_spCount:
            self.restoreState()
            return dashText,False
        dashText = self.dashText
        return dashText,True

    def punctuation(self, punctuation):
        if not self.curChClass & self.PUNCTUATUON:
            return punctuation,False

        self.saveState()
        punctuation = self.curCh
        self.getCh()

        #Проверяем ... и !!! и ?.. и !..
        if punctuation == '.' and self.curCh == '.':
            while self.curCh == '.':
                self.getCh()
            punctuation = self.dotes
        elif punctuation == '!' and self.curCh == '!':
            while self.curCh == '!':
                self.getCh()
            punctuation = '!!!'
        elif (punctuation == '?' or punctuation == '!') and self.curCh == '.':
            while self.curCh == '.':
                self.getCh()
            punctuation = '..'

        #Далее идёт слово - добавляем пробел
        if self.curChClass & self.RUS:
            if punctuation != '.':
                punctuation += ' '
            return punctuation,True
        elif (self.curChClass & self.SPACE) or (self.curChClass & self.NL) or not self.curChClass:
            return punctuation,True
        else:
            self.restoreState()
            return punctuation,False


    def number(self, num):
        if not (self.curChClass & self.NUMERIC) == self.NUMERIC:
            return num,False

        num = self.curCh

        while (self.curChClass & self.NUMERIC) == self.NUMERIC:
            num += self.curCh
            self.getCh()

        return num,True


    def html_entity_decode_char(m, defs=htmlentitydefs.entitydefs):
        try:
            return defs[m.group(1)]
        except KeyError:
            return m.group(0)


    def htmlEntity(self, entityCh):
        if self.curCh != u'&':
            return entityCh,False

        self.saveState()
        self.matchCh(u'&')
        pattern = re.compile(u"&(\w+?);")
        if self.matchCh(u'#'):
            entityCode = 0
            newEntityCode,boolEntityCode = self.number(entityCode)
            if boolEntityCode or not self.matchCh(';'):
                entityCode = newEntityCode
                self.restoreState()
                return entityCh,False
            entityCode = pattern.sub(self.html_entity_decode_char, u"&#%s;" & entityCode)
            return entityCh,True
        else:
            entityName = u''
            entityName, bool_name = self.name(entityName)
            if not bool_name or not self.matchCh(u';'):
                self.restoreState()
                return entityCh,False

            entityCh = pattern.sub(self.html_entity_decode_char, u"&#%s;" & entityName)
            return entityCh,False


    def quote(self, spacesBefore,  quote, closed):
        self.saveState()
        quote = self.curCh
        self.getCh()

        if self.quotesOpened == 0 and not (self.curChClass & self.ALPHA or self.curChClass & self.NUMERIC):
            self.restoreState()
            return quote, closed, False

        closed = (self.quotesOpened >=2) or (self.quotesOpened > 0 and (not spacesBefore or self.curChClass & self.SPACE or self.curChClass & self.PUNCTUATUON))

        return (quote, closed, True)



    def makeQuote(self, closed, level):
        levels = len(self.textQuotes)
        if level > levels:
            level = levels

        return self.textQuotes[level][1 if closed  else 0]

    def skipSpaces(self, count = 0):
        while self.curChClass == self.SPACE:
            self.getCh()
            count += 1

        return count, (count > 0)


    def textFunction(self, text):
        text = u''
        dashText = u''
        newLine = True
        newWord = True
        url = None
        href = None

        typoEnabled = not self.noTypoMode

        while self.curCh != '<' and self.curChClass:
            brCount = 0;
            spCount = 0;
            quote = None;
            closed = None;
            punctuation = None;
            entity = None;

            spCount, bool_spCount = self.skipSpaces(spCount)


            bool_entity = False
            if spCount and self.curCh == u'&':
                entity,bool_entity = self.htmlEntity(entity)
            if bool_entity:
                text += self.entities2[entity] if self.entities2.has_key(entity) else entity
                continue

            bool_punctuation = False
            if typoEnabled and (self.curChClass & self.PUNCTUATUON):
                punctuation,bool_punctuation = self.punctuation(punctuation)
            if  bool_punctuation:
                if spCount and punctuation == '.' and (self.curChClass & self.LAT):
                    punctuation = u' ' + punctuation
                text += punctuation
                newWord = True
                continue

            bool_dash = False
            if typoEnabled and (spCount or newLine) and self.curCh==u'-':
                dashText,bool_dash = self.dash(dashText)
            if bool_dash:
                text += dashText
                newWord = True
                continue

            boolQuote = False
            if typoEnabled and (self.curChClass & self.HTML_QUOTE):
                quote, closed, boolQuote = self.quote(spCount, quote, closed)
            if boolQuote:
                self.quotesOpened += -1 if closed else 1
                if self.quotesOpened<0:
                    closed = False
                    self.quotesOpened = 1
                quote = self.makeQuote(closed, self.quotesOpened if closed else self.quotesOpened-1)
                if spCount:
                    quote = u' ' + quote
                text += quote
                newWord = True
                continue

            if spCount>0:
                text += u' '
                newWord = True
                continue

            bool_brCount = False
            if self.isAutoBrMode:
                brCount, bool_brCount = self.skipNL(brCount)
            if bool_brCount:
                if self.curParentTag and self.tagsRules.has_key(self.curParentTag) and self.tagsRules[self.curParentTag].has_key(self.TR_TAG_NO_AUTO_BR) and (self.openedTag or (self.tagsRules.has_key(self.openedTag) and self.tagsRules[self.openedTag].has_key(self.TR_TAG_NO_AUTO_BR))):
                    True
                else:
                    br = self.br + self.nl
                    text += br if brCount == 1 else br + br
                newLine = True
                newWord = True
                continue

            retUrl = False
            if newWord and self.isAutoLinkMode and (self.curChClass & self.LAT) and self.openedTag!='a':
                url, href, retUrl = self.url(url, href)
            if retUrl:
                text += self.makeTag(u'a', {u'href':href}, url, False)
                continue


            if  self.curChClass & self.PRINATABLE:
                text += self.entities2[self.curCh] if self.entities2.has_key(self.curCh) else self.curCh
                self.getCh()
                newLine = False
                newWord = False
                continue


            self.getCh()



        self.skipSpaces()
        return text, (text != u'')


    def url(self, url, href):
        self.saveState()
        url = u''
        urlChMask = self.URL | self.ALPHA | self.PUNCTUATUON

        if self.matchStr('http://'):
            while self.curChClass & urlChMask:
                url += self.curCh
                self.getCh()

            if not len(url):
                self.restoreState()
                return (url, href, False)

            href = u'http://' + url
            return (url, href, True)
        elif self.matchStr(u'https://'):
            while self.curChClass & urlChMask:
                url += self.curCh
                self.getCh()

            if not len(url):
                self.restoreState()
                return (url, href, False)

            href = u'https://' + url
            return (url, href, True)
        elif self.matchStr(u'www.'):
            while self.curChClass & urlChMask:
                url += self.curCh
                self.getCh()

            if not len(url):
                self.restoreState()
                return (url, href, False)

            href = u'https://www.' + url
            return (url, href, True)

        self.restoreState()
        return (url, href, False)

    def eror(self, message):

        self.errors.append({
            u'message' : message,
            u'pos'     : self.curPos,
            u'ch'      : self.curCh,
            u'line'    : 0,
            #'str'     : $str,
        })



















