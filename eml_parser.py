from email import message_from_file
import os


def file_exists (f):
    return os.path.exists(os.path.join(path, f))


def disqo (s):
    s = s.strip()
    if s.startswith("'") and s.endswith("'"): return s[1:-1]
    if s.startswith('"') and s.endswith('"'): return s[1:-1]
    return s


def disgra (s):
    s = s.strip()
    if s.startswith("<") and s.endswith(">"): return s[1:-1]
    return s


def split_line(s):
    s = s.splitlines()
    return s 


def pullout (m, key):

    Text = ""

    if not m.is_multipart():
        if m.get_filename(): 
            fn = m.get_filename()
            return Text

        cp = m.get_content_type()
        if cp == "text/plain": Text += m.get_payload(decode=True)
        else:
            cp = m.get("content-type")
            o = cp.find("name=")
            if o == -1: return Text
            ox = cp.find(";", o)
            if ox == -1: ox = None
            o += 5; fn = cp[o:ox]
            fn = disqo(fn)
        return Text

    y = 0
    while 1:
        try:
            pl = m.get_payload(y)
        except: break
        t = pullout(pl, key)
        Text += t
        y += 1
    return Text


def extract (msgfile, key):
    m = message_from_file(msgfile)
    Subject = caption(m)
    Text = pullout(m, key)
    Text = Text.strip()
    Text = split_line(Text)
    word_list = []
    label_value = 0
    foo = open('Label of eml ', 'a')
    for line in Text:
        for word in line.split():
            word_list.append(word)
    # print("Word List : ",word_list)
    
    # For now we have just two different word matcher
    matchers = ['stage', 'emploi']
    matching = [s for s in word_list if any(xs in s for xs in matchers)]
    
    if(not matching):
        label_value = 0
    else:
        label_value = 1 
    foo.write(key + ": " + str(label_value) + '\n')
    
    msg = {"Subject": Subject, "Text": Text}
    return msg


def caption (origin):
    Subject = ""
    if origin.has_key("subject"): Subject = origin["subject"].strip()
    return Subject


import glob
path = 'C:/Users/etalay/eclipse-workspace/Eml File Classifer/eml/*.eml'

files = glob.glob(path)

for name in files:
        with open(name, 'r') as f:
            print extract(f, f.name)
