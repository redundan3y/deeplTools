import json
import os
import re
import urllib.parse
import urllib.request

DEEPL_TRANSLATE_EP = 'https://api.deepl.com/v2/translate'
source_path = "./Source"
target_path = "./Translation"

def traverseDirectory(path):
    dic = os.walk(path)
    file = []
    for files in dic:
        file = files
    return file[2]

def translate(text, s_lang='EN', t_lang='PL'):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; utf-8'
    }

    params = {
        'auth_key': 'e8556d86-270d-c623-27a2-2500d125c122',
        'text': text,
        'target_lang': t_lang
    }

    if s_lang != '':
        params['source_lang'] = s_lang

    req = urllib.request.Request(
        DEEPL_TRANSLATE_EP,
        method='POST',
        data=urllib.parse.urlencode(params).encode('utf-8'),
        headers=headers
    )

    try:
        with urllib.request.urlopen(req) as res:
            res_json = json.loads(res.read().decode('utf-8'))
            #print(json.dumps(res_json, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(e)

    return(res_json)


def readFile(filepath):
    f = open(filepath, "r")
    Lines = f.readlines()
    # i = 2
    # for line in Lines:
    #     if re.match('^[^0-9][a-zA-Z0-9_]+$', line):
    #         print("te")
    #     print(line)
    f.close()
    return Lines

def divideLines(Lines):
    counter = 0
    testcounter = 1

    timelapse_list = []
    sentence_list = []
    sentence_lenth_list = []
    lines_per_time = []

    # lines_per_time = []

    temp_centence = ''
    for idx, line in enumerate(Lines):
        if str.isdigit(line.strip('\n')):
            pass
        elif re.match("[0-9]+.*", line):
            testcounter = testcounter + 1
            if testcounter == 17:
                print("yes")
            timelapse_list.append(line.strip())
            pass
        elif re.search("\.|\?", line):
            print(line)
            counter = counter + 1
            temp_centence = temp_centence + line.strip()
            sentence_list.append(temp_centence)
            sentence_lenth_list.append(counter)
            temp_centence = ''
            counter = 0
            if Lines[idx + 1].isspace() and re.match("[0-9]+.*", Lines[idx - 1]):
                lines_per_time.append(1)
            elif not Lines[idx + 1].isspace() and  re.match("[0-9]+.*", Lines[idx - 1]):
                lines_per_time.append(2)
        elif re.match("\\n", line):
            pass
        elif re.match('\\ufeff1', line):
            pass
        else:
            print(line)
            temp_centence = temp_centence + line.strip() + ' '
            counter = counter + 1

            if Lines[idx + 1].isspace() and re.match("[0-9]+.*", Lines[idx - 1]):

                lines_per_time.append(1)
            elif Lines[idx + 1].isspace() and not re.match("[0-9]+.*", Lines[idx - 1]):
                pass
            else:
                lines_per_time.append(2)

    return timelapse_list, sentence_list, sentence_lenth_list, lines_per_time


def translateSentence(sentence_list):
    translate_sentence = []
    for sentence in sentence_list:
        response = translate(sentence)
        translate_sentence.append(response['translations'][0]['text'])
        print(response['translations'][0]['text'])
    return translate_sentence

def divideTranslatedSentence(translate_sentence, sentence_lenth_list):
    translate_sentence_divide = []
    counter = 0
    for sentence in translate_sentence:
        temp_centence = ''
        words_counter = 0

        divided_sentence = sentence.split()
        sentence_word_lenth = len(divided_sentence)
        words_per_time = int(sentence_word_lenth / sentence_lenth_list[counter])
        counter = counter + 1
        # print(divided_sentence)
        for words in divided_sentence:
            if words_counter == words_per_time:
                # print(temp_centence)
                words_counter = 0
                translate_sentence_divide.append(temp_centence)
                temp_centence = '' + words + ' '

            else:
                temp_centence = temp_centence + words + ' '
                words_counter = words_counter + 1
        translate_sentence_divide.append(temp_centence)
    return translate_sentence_divide

def saveTranslation(dividedTranslation, timelapse_list, file_name, lines_per_time):

    f = open(target_path + "/" + file_name, "w")

    counter = 0
    timecounter = 0
    for linespertime in lines_per_time:
        if linespertime == 1:

            f.write(timelapse_list[timecounter] + "\n")
            try:
                f.write(dividedTranslation[counter] + "\n\n")
            except (IndexError) :
                print("One line shorter")
            counter = counter + 1
        if linespertime == 2:
            f.write(timelapse_list[timecounter] + "\n")
            try:
                f.write(dividedTranslation[counter] + "\n")
                f.write(dividedTranslation[counter + 1] + "\n\n")

            except (IndexError) :
                print("One line shorter")
            counter = counter + 2
        timecounter = timecounter + 1
    f.close()
    print("Process Complete!")

def translateProcess(file_name):
    Lines = readFile(file_name)

    divideResult = divideLines(Lines)
    timelapse_list = divideResult[0]
    sentence_list = divideResult[1]
    sentence_lenth_list = divideResult[2]

    translate_sentence = translateSentence(sentence_list)
    dividedTranslation = divideTranslatedSentence(translate_sentence, sentence_lenth_list)
    saveTranslation(dividedTranslation, timelapse_list)

def generateOutputFilename(src_file_fame):
    output_filename = ''
    split = src_file_fame.split(".")
    split.insert(0, "[PL] ")
    flag = 0
    for words in split:
        if flag == 0:
            output_filename = output_filename + words
            flag = 1
        else:
            output_filename = output_filename + words + '.'
    return output_filename.rstrip('.')

def checkIfFileExsist(filename):
    return os.path.exists(target_path + '/' + filename)

def tranlatingProcess(filename):
    Lines = readFile(source_path + '/' + filename)

    divideResult = divideLines(Lines)
    timelapse_list = divideResult[0]
    sentence_list = divideResult[1]
    sentence_lenth_list = divideResult[2]
    lines_per_time = divideResult[3]

    translate_sentence = translateSentence(sentence_list)
    dividedTranslation = divideTranslatedSentence(translate_sentence, sentence_lenth_list)
    print(len(dividedTranslation))
    total = 0

    file_name = generateOutputFilename(file)
    saveTranslation(dividedTranslation, timelapse_list, file_name, lines_per_time)
    print(lines_per_time)


if __name__ == '__main__':
    # Lines = readFile(srt_file)
    #
    # divideResult = divideLines(Lines)
    # timelapse_list = divideResult[0]
    # sentence_list = divideResult[1]
    # sentence_lenth_list = divideResult[2]
    #
    # translate_sentence = translateSentence(sentence_list)
    # dividedTranslation = divideTranslatedSentence(translate_sentence, sentence_lenth_list)
    # saveTranslation(dividedTranslation, timelapse_list)

    # Lines = readFile("./Source/BMA Sugarfina Intro USA intro_SD_WEB.mp4.txt")
    # print(Lines)
    # divideResult = divideLines(Lines)
    # timelapse_list = divideResult[0]
    # sentence_list = divideResult[1]
    # sentence_lenth_list = divideResult[2]
    # print(sentence_lenth_list)
    # total = 0
    #
    # translate_sentence = translateSentence(sentence_list)
    #
    # dividedTranslation = divideTranslatedSentence(translate_sentence, sentence_lenth_list)
    #
    # for i in sentence_lenth_list:
    #     total = total + i
    # print(total)
    # print(len(dividedTranslation))
    # tranlatingProcess()
    # for idx, lines in enumerate(lines_per_time):
    #     print(timelapse_list[idx])
    #     print(lines)

    files = traverseDirectory(source_path)
    for file in files:
        if checkIfFileExsist(generateOutputFilename(file)):
            print(file + " has been translated!\n")
            pass
        else:
            tranlatingProcess(file)