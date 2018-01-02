from email import message_from_file
import os

def file_exists (f):
    return os.path.exists(os.path.join(path, f))

def save_file (fn, cont):
    file = open(os.path.join(path, fn), "wb")
    file.write(cont)
    file.close()

def construct_name (id, fn):
    id = id.split(".")
    id = id[0]+id[1]
    return id+"."+fn

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
    
    """Extracts content from an e-mail message.
    This works for multipart and nested multipart messages too.
    m   -- email.Message() or mailbox.Message()
    key -- Initial message ID (some string)
    Returns tuple(Text, Html, Files, Parts)
    Text  -- All text from all parts.
    Html  -- All HTMLs from all parts
    Files -- Dictionary mapping extracted file to message ID it belongs to.
    Parts -- Number of parts in original message.
    """
    Html = ""
    Text = ""
    Files = {}
    Parts = 0
    if not m.is_multipart():
        if m.get_filename(): # It's an attachment
            fn = m.get_filename()
            cfn = construct_name(key, fn)
            Files[fn] = (cfn, None)
            if file_exists(cfn): return Text, Html, Files, 1
            save_file(cfn, m.get_payload(decode=True))
            return Text, Html, Files, 1
        # Not an attachment!
        # See where this belongs. Text, Html or some other data:
        cp = m.get_content_type()
        if cp=="text/plain": Text += m.get_payload(decode=True)
        elif cp=="text/html": Html += m.get_payload(decode=True)
        else:
            # Something else!
            # Extract a message ID and a file name if there is one:
            # This is some packed file and name is contained in content-type header
            # instead of content-disposition header explicitly
            cp = m.get("content-type")
            try: id = disgra(m.get("content-id"))
            except: id = None
            # Find file name:
            o = cp.find("name=")
            if o==-1: return Text, Html, Files, 1
            ox = cp.find(";", o)
            if ox==-1: ox = None
            o += 5; fn = cp[o:ox]
            fn = disqo(fn)
            cfn = construct_name(key, fn)
            Files[fn] = (cfn, id)
            if file_exists(cfn): return Text, Html, Files, 1
            save_file(cfn, m.get_payload(decode=True))
        return Text, Html, Files, 1
    # This IS a multipart message.
    # So, we iterate over it and call pullout() recursively for each part.
    y = 0
    while 1:
        # If we cannot get the payload, it means we hit the end:
        try:
            pl = m.get_payload(y)
        except: break
        # pl is a new Message object which goes back to pullout
        t, h, f, p = pullout(pl, key)
        Text += t; Html += h; Files.update(f); Parts += p
        y += 1
    return Text, Html, Files, Parts

def extract (msgfile, key):
    """Extracts all data from e-mail, including From, To, etc., and returns it as a dictionary.
    msgfile -- A file-like readable object
    key     -- Some ID string for that particular Message. Can be a file name or anything.
    Returns dict()
    Keys: from, to, subject, date, text, html, parts[, files]
    Key files will be present only when message contained binary files.
    For more see __doc__ for pullout() and caption() functions.
    """
    m = message_from_file(msgfile)
    Subject= caption(m)
    Text, Html, Files, Parts = pullout(m, key)
    Text = Text.strip(); Html = Html.strip()
    Text = split_line(Text)
    word_list = []
    label_value = 0
    foo = open('Label of eml ', 'a')
    
    for line in Text:
        for word in line.split():
            word_list.append(word)
    print("Word List : ",word_list)
    
    matchers = ['Visualiser', 'rachat']
    matching = [s for s in word_list if any(xs in s for xs in matchers)]
    
    if( not matching):
        label_value = 0
    else:
        label_value = 1 
    foo.write(str(word_list)+'\n'+ str(label_value)+'\n')
    
    
    
  

    
    
    msg = {"Subject": Subject,"Text": Text}
    #if Files: msg["files"] = Files
    return msg

def caption (origin):
    Subject = ""
    if origin.has_key("subject"): Subject = origin["subject"].strip()
    return Subject


import glob
path = 'C:/Users/etalay/eclipse-workspace/Jupyter_Pise/eml/*.eml'
files = glob.glob(path)


for name in files:
        with open(name,'r') as f:
            print extract(f, f.name)
            
            
            

