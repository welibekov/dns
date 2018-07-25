#!/usr/bin/env python3

import socket
import binascii
from dnslib import DNSRecord,DNSHeader,RR,TXT
from weather import Weather,Unit

ip = "127.0.0.1"
port = 15353

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((ip, port))

def parse_request(data):
	request = DNSRecord.parse(data)
	fqdn = [x.decode() for x in (request.q.qname.label)]
	domain = '.'.join(fqdn[-2:])
	city = '.'.join(fqdn[:-2])
	if wttr_in(domain):

		ID=request.header.id
		RQ=request.q
		QN=request.q.qname
		QT=request.q.qtype

		MSG=get_weather(city)
		if MSG is None:
			MSG="No city found, try: baku,moscow,nackhichevan"
		reply=DNSRecord(DNSHeader(id=ID,qr=1,aa=1,ra=1),q=RQ)
		reply.add_answer(RR(QN,QT,rdata=TXT(MSG)))
		return reply.pack()
	else:
		return False

"""	
def reply_request(query):
	if query:
		reply=DNSRecord(DNSHeader(id=query[0],qr=1,aa=1,ra=1),q=query[1])
		reply.add_answer(RR(query[2],query[3],rdata=TXT("test")))
		
		return reply.pack()
"""

def wttr_in(domain):
	return domain == 'wttr.in'

def get_weather(city):
	weather = Weather(unit=Unit.CELSIUS)
	l = weather.lookup_by_location(city)
	if l is None:
		return None
	else:
		weather_report = "City:{},Temp:{},Sky:{},Humiditi:{}".format(city,l.condition.temp,
																l.condition.text,
																l.atmosphere['humidity'])
		return str(weather_report)

while 1:
	data, addr = sock.recvfrom(512)
	#sock.sendto(reply_request(parse_request(data)), addr)
	sock.sendto(parse_request(data), addr)
	
