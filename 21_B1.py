import csv

def getPropIndex(data, propListString):
    propList = list()
    # Tách tên các property từ string
    propListStringSplited = propListString[1:-1].split(',')
    # Lấy index của các property này trong data
    for prop in propListStringSplited:
        propList.append(data[0].index(prop))
    return propList

def minMaxNorm(data, command, propListString):
    # Lấy index của các property được chỉ định
    try:
        propList = getPropIndex(data, propListString)
    except Exception:
        print('[Error] No such properties')
        return []
    # Chuyển vị data để thuận tiện xử lý
    data = [[row[i] for row in data] for i in range(len(data[0]))]
    # Tham số newMin, newMax
    minMaxPos = command.index('--newminmax') + 1
    newMin, newMax = list(eval(command[minMaxPos]))
    # Với mỗi property, tìm min và max, thực hiện mapping qua phép ánh xạ f(x)
    for prop in propList:
        oldMin, oldMax = min(data[prop][1:]), max(data[prop][1:])
        f = lambda x: (x - oldMin) / (oldMax - oldMin) * (newMax - newMin) + newMin
        data[prop][1:] = list(map(f, data[prop][1:]))
    # Chuyển vị lại data ban đầu
    data = [[row[i] for row in data] for i in range(len(data[0]))]
    return data

def zScoreNorm(data, propListString):
    # Lấy index của các property được chỉ định
    try:
        propList = getPropIndex(data, propListString)
    except Exception:
        print('[Error] No such properties')
        return []
    # Chuyển vị data để thuận tiện xử lý
    data = [[row[i] for row in data] for i in range(len(data[0]))]
    # Với mỗi property, tính mean và deviation, thực hiện mapping qua phép ánh xạ f(x)
    for prop in propList:
        mean = sum(data[prop][1:]) / (len(data[prop]) - 1)
        deviant = 0
        for v in range(len(data[prop]) - 1):
            deviant += abs(data[prop][v + 1] - mean)
        deviant /= len(data[prop]) - 1
        f = lambda x: (x - mean) / deviant
        data[prop][1:] = list(map(f, data[prop][1:]))
    # Chuyển vị lại data ban đầu
    data = [[row[i] for row in data] for i in range(len(data[0]))]
    return data

def widthBin(data, command, propListString):
    try:
        propList = getPropIndex(data, propListString)
    except Exception:
        print('[Error] No such properties')
        return []
    binPos = command.index('--bin') + 1
    binCount = int(command[binPos])
    pData = [[row[i] for row in data] for i in range(len(data[0]))]
    for prop in propList:
        propMin, propMax = min(pData[prop][1:]), max(pData[prop][1:])
        binRange = (propMax - propMin) / binCount
        for inst in range(len(data) - 1):
            binIndex = int((data[inst + 1][prop] - propMin) // binRange)
            propBinLower = propMin + binIndex * binRange
            if data[inst + 1][prop] != propMax:
                data[inst + 1] += ['[{},{})'.format(propBinLower, propBinLower + binRange)]
            else:
                data[inst + 1] += ['[{},{}]'.format(propMax - binRange, float(propMax))]
        data[0] += [data[0][prop] + 'Bin']
    return data

def depthBin(data, command, propListString):
    try:
        propList = getPropIndex(data, propListString)
    except Exception:
        print('[Error] No such properties')
        return []
    binPos = command.index('--bin') + 1
    binCount = int(command[binPos])
    eleCount = int((len(data) - 1) // binCount) + 1
    for prop in propList:
        data[1:] = sorted(data[1:], key = lambda ele: ele[prop])
        binEdge = [0] * (binCount + 1)
        for binIndex in range(binCount):
            binEdge[binIndex + 1] = min(eleCount * (binIndex + 1), len(data) - 1)
        while True:
            for binIndex in range(binCount, 1, -1):
                if binEdge[binIndex] - binEdge[binIndex - 1] < eleCount - 1:
                    binEdge[binIndex - 1] -= eleCount - 1 - (binEdge[binIndex] - binEdge[binIndex - 1])
                    continue
            break
        for binIndex in range(binCount):
            for inst in range(binEdge[binIndex], binEdge[binIndex + 1]):
                data[inst + 1] += ['[{},{}]'.format(data[binEdge[binIndex] + 1][prop], data[binEdge[binIndex + 1]][prop])]
        data[0] += [data[0][prop] + 'DepthBin']
    return data

def remove(data, propListString):
    # Lấy index của các property được chỉ định
    try:
        propList = getPropIndex(data, propListString)
    except Exception:
        print('[Error] No such properties')
        return []
    # Với mỗi property, instance nào không bị trống property này (nghĩa là instance hợp lệ) thì được copy vào biến pData
    pData = list()
    for prop in propList:
        pData = [data[0]]
        for inst in range(len(data) - 1):
            if data[inst + 1][prop] not in ['', []]:
                pData += [data[inst + 1]]
        data = pData
    return pData

def fillIn(data, propList):
    # Lấy index của các property được chỉ định
    try:
        propList = getPropIndex(data, propListString)
    except Exception:
        print('[Error] No such properties')
        return []
    # Với mỗi property, tính mean (đối với kiểu numeric) hoặc mode (đối với kiểu non-numeric) rồi điền vào chỗ còn khuyết
    pData = remove(data, propListString)
    pData = [[row[i] for row in pData] for i in range(len(pData[0]))]
    for prop in propList:
        try:
            # Thuộc tính numeric
            mean = sum(pData[prop][1:]) / (len(pData[prop]) - 1)
            for inst in range(len(data) - 1):
                if data[inst + 1][prop] in ['', []]:
                    data[inst + 1][prop] = mean
        except Exception:
            # Thuộc tính non-numeric
            count = [[pData[prop][1:].count(value), value] for value in set(pData[prop][1:])]
            count.sort()
            for inst in range(len(data) - 1):
                if data[inst + 1][prop] in ['', []]:
                    data[inst + 1][prop] = count[-1][1]
    return data

while True:
    data = list()

    # Đọc command, tách từ, chuyển chữ hoa sang chữ thường ngoại trừ propList
    command = input('Command> ').split()
    commandLen = len(command)
    for i in range(commandLen - 1):
        if command[i] != '--proplist':
            command[i + 1] = command[i + 1].lower()
    command[0] = command[0].lower()

    # Command 'exit', thoát chương trình
    if command[0] == 'exit':
        break

    # Command 'preprocess', thực thi chương trình
    elif command[0] == 'preprocess':
        # Tìm vị trí các tham số '--input', '--output', '--task', '--propList'
        try:
            inputPos = command.index('--input') + 1
            outputPos = command.index('--output') + 1
            taskPos = command.index('--task') + 1
            propPos = command.index('--proplist') + 1
            if inputPos >= commandLen or outputPos >= commandLen or taskPos >= commandLen or propPos >= commandLen:
                raise IndexError
        except Exception:
            print('[Error] Are you missing some arguments?')
            continue

        # Mở file input
        try:
            fint = open(command[inputPos], 'r', encoding = 'utf-8-sig')
        except Exception:
            print('No such files or directories.')
            continue

        # Đọc dữ liệu vào biến data, chuyển chuỗi sang số, đóng file input
        for row in csv.reader(fint):
            for prop in range(len(row)):
                try:
                    row[prop] = eval(row[prop])
                except Exception:
                    pass
            data += [row]
        fint.close()

        # Xử lý
        propListString = command[propPos]
        try:
            if command[taskPos] == 'minmaxnorm': # Chuẩn hóa min - max
                data = minMaxNorm(data, command, propListString)
            elif command[taskPos] == 'zscorenorm': # Chuẩn hóa z-score
                data = zScoreNorm(data, propListString)
            elif command[taskPos] == 'widthbin': # Chia giỏ theo chiều rộng
                data = widthBin(data, command, propListString)
            elif command[taskPos] == 'depthbin': # Chia giỏ theo chiều sâu
                data = depthBin(data, command, propListString)
            elif command[taskPos] == 'remove': # Xóa mẫu thiếu dữ liệu
                data = remove(data, propListString)
            elif command[taskPos] == 'fillin': # Điền giá trị bị thiếu
                data = fillIn(data, propListString)
            else:
                print('[Error] Unknown task.')
        except TypeError:
            print('[Error] Some properties are not numeric.')
            continue
        except Exception:
            print('[Error] Are you missing some arguments?')
            continue

        # Ghi data ra file output và đóng file
        if data != []:
            fout = open(command[outputPos], 'w', encoding = 'utf-8-sig', newline = '')
            csv.writer(fout).writerows(data)
            fout.close()

    # Lỗi command
    else:
        print('[Error] Unknown command.')
