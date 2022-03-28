
def csv_file_reader(filename):
	l = []
	f = open(filename, 'r')
	data = f.read()
	f.close()
	data = data.split('\n')
	for i in data:
		new = i.split(',')
		l.append(new)
	l.pop()
	return l
	
def csv_data_reader(csv_data):
	l = []
	data = csv_data.split('\n')
	for i in data:
		new = i.split(',')
		l.append(new)
	l.pop()
	return l

if __name__ == "__main__":
	print(csv())
	f = open("new", "w")
	f.write(str(csv()))
	f.close()
