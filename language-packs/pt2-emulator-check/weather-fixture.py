import socket,time,struct,uuid
from libpebble2.communication import PebbleConnection
from libpebble2.communication.transports.qemu import QemuTransport
from libpebble2.protocol.blobdb import BlobCommand,InsertCommand,BlobResponse
s=socket.socket(socket.AF_UNIX);s.connect('cmake-build-matrix/qemu_emery-normal/qemu-mon.sock');s.recv(8192);s.sendall(b'cont\n');s.close()
p=PebbleConnection(QemuTransport(port=12444));p.connect();p.run_async();p._app_version_response(None);time.sleep(1);print('language',p.watch_info.language,flush=True)
k=uuid.UUID('23456789-1234-5678-abcd-123456789012').bytes
b=struct.pack('<BhBhhBhhiBBhhhHHhhB',4,18,3,21,13,0,18,11,int(time.time()),1,5,17,50,80,12,45,5008,1442,7)
for i,t in enumerate([3,0,1,8,4,2,7]): b+=struct.pack('<hhB',21-i,13-i,t)
b+=bytes([24])+bytes([3]*24)+bytes([18]*24)
b+=struct.pack('<h',120)+bytes([80,12,50]*7)
b+=struct.pack('<BBHH',61,85,5000,8)+struct.pack('<7h',17,16,15,14,13,12,11)
b+=struct.pack('<8h',45,45,90,135,180,225,270,315)+bytes([50]*24)
b+=bytes([24])+bytes([0]*24)+bytes([16]*24)
assert len(b)==250,len(b)
strings=b''
for txt in ['Praha – Žižkov','Light Rain']:
 v=txt.encode();strings+=struct.pack('<H',len(v))+v
b+=struct.pack('<H',len(strings))+strings
for token,db,key,val in [(1,5,k,b),(2,9,b'weatherApp',bytes([1])+k)]:
 result=p.send_and_read(BlobCommand(token=token,database=db,content=InsertCommand(key=key,value=val)),BlobResponse)
 print(db,result,flush=True)
