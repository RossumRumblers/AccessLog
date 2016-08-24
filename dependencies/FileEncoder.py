from datetime import *

def _encodeID(did):
	r = ""
	if len(did) == 10:
		for e in [did[:5],did[5:]]:
			s = hex(int(e))[2:]
			r += str(s if len(s) is 5 else "0000"[:5 - len(s)] + s)
		return r
	return None

def _decodeID(eid):
	r = ""
	for e in [eid[:5],eid[5:]]:
		l = 0
		while e[l] == 0 : l+=1
		r += str(int(e[:5-l], 16))
	return r

def _encodeLine(DT, IDnum):
	#mdd0HMMSSIIIIIIIIII
	#DT = datetime.now()
	month  = hex(DT.month)[2:]
	day    = hex(DT.day)[2:]
	mod    = 1 if DT.hour % 12 != DT.hour else 0
	hour   = hex(DT.hour % 12)[2:]
	minute = hex(DT.minute)[2:]
	second = hex(DT.second)[2:]
	eid    = _encodeID(IDnum)

	Line = "{0}{1}{2}{3}{4}{5}{6}".format(
		month,
		day,
		mod,
		hour,
		minute,
		second,
		eid
	)
	return Line

def _decodeLine(Line):
	#mdd0HMMSSIIIIIIIIII

	#prepend a 0 to numbers of length 1
	pre = lambda x: "0" + str(x) if len(str(x)) == 1 else str(x)

	year = datetime.now().year
	month  = pre(int(Line[0],   16))   # m
	day    = pre(int(Line[1:3], 16))   # d
	mod    =     int(Line[3],   16)    # 0
	hour   =     int(Line[4],   16)    # H
	minute = pre(int(Line[5:7], 16))   # MM
	second = pre(int(Line[7:9], 16))   # SS
	eid    =         Line[9:]          # IIIIIIIIII

	hour = pre(str(int(hour) + (int(mod) * 12)))

	logdate = "{0}-{1}-{2} {3}:{4}:{5}".format(
		year,
		month,
		day,
		hour,
		minute,
		second
	)
	return([datetime.strptime(logdate, "%Y-%m-%d %H:%M:%S"),_decodeID(eid)])

def writeLine(DT, IDnum, File):
	f = file.open



if __name__ == "__main__":
	l = _encodeLine(datetime.now(),"1207467036")
	print(l)
	s = _decodeLine(l)
	print(s[0], s[1])