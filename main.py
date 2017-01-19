import nntplib
from datetime import datetime, timedelta
import dateutil.parser
import facebook

#Put your Facebook access token here, prefer long-lived token
fb_access_token = 'fb_token'
#Facebook group id to post
groupdid = 'group_id'

user_fac = 'user'
pass_fac = 'pass'


def postToFacebook(Message=None):
    graph = facebook.GraphAPI(access_token=fb_access_token, version='2.7')
    graph.put_object(parent_object=groupdid, connection_name='feed',
                 message=Message)

groups =  ['lstinfo.officiel','lstinfo']
msg_id = set()
if __name__ == '__main__':
    s = nntplib.NNTP_SSL("news.u-bordeaux.fr",563,user_fac,pass_fac)
    f = open('.lastaccess', 'r+')
    f.seek(0,0)
    buf = f.readline()
    last_access = dateutil.parser.parse(buf)
    today = datetime.now()
    f.seek(0,0)
    buf = today.isoformat()
    size = f.write(buf)
    f.truncate(size)
    f.close()
    for group in groups :
        resp, articles = s.newnews(group, last_access)
        for art in articles:
            response, info = s.body(art)
            response, head = s.head(art)
            user = str(head.lines[1],"utf8")[6:]
            text = False
            original = True
            datePosted = "Erreur"
            charset = 'utf-8'
            for line in head.lines:
                line = str(line,"utf8")
                if(line.startswith('Content-Type: text/plain')):
                    print(line)
                    text = True
                    occur = line.find('charset=')
                    if occur != -1:
                        pos = occur + len('charset=')
                        end = line.find(';',pos)
                        charset = str(line[pos:end if end != -1 else len(line)])
                        print(charset)
                if(line.startswith('Date:')):
                    datePosted = line[6:]
                if (line.startswith('In-Reply-To')):
                    original = False
                if (nntplib.decode_header(line).startswith('Subject: Re')):
                    original = False
                if (line.startswith('Message-ID')):
                    curr = len(msg_id)
                    msg_id.add(line[12:])
                    if len(msg_id) == curr:
                        original = False
            if original:
                msg = "NewsBot: Message de " + nntplib.decode_header(user) + " depuis " + group + " à " + datePosted + ":\n"
                if text:
                    for i in info.lines:
                        try :
                            msg += i.decode(charset,'ignore') + '\n'
                        except UnicodeDecodeError as e:
                            print(e)
                            msg += "Can't decode" + '\n'
                else :
                    msg+= "Message non reconnu"

                print(msg,"\n")
                postToFacebook(msg)
