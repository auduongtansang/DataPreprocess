import argparse
import sys
import csv

def getPropIndex(data, propListString):
    propList = list()
    propListString = propListString.lstrip('{').rstrip('}')
    # Tách tên các property từ string
    propListStringSplited = propListString.split(',')
    # Lấy index của các property này trong data
    try:
        for prop in propListStringSplited:
            propList.append(data[0].index(prop))
    except ValueError:
        print('No such properties')
        sys.exit()
    return propList

def minMaxNorm(data, args):
    # Lấy index của các property được chỉ định
    propList = getPropIndex(data, ','.join(args.prop))
    # Chuyển vị data để thuận tiện xử lý
    data = [[row[i] for row in data] for i in range(len(data[0]))]
    # Tham số newMin, newMax
    newMin, newMax = [eval(x) for x in args.newMinMax]
    # Với mỗi property, tìm min và max, thực hiện mapping qua phép ánh xạ f(x)
    for prop in propList:
        oldMin, oldMax = min(data[prop][1:]), max(data[prop][1:])
        f = lambda x: (x - oldMin) / (oldMax - oldMin) * (newMax - newMin) + newMin
        data[prop][1:] = list(map(f, data[prop][1:]))
    # Chuyển vị lại data ban đầu
    data = [[row[i] for row in data] for i in range(len(data[0]))]
    return data

def zScoreNorm(data, args):
    # Lấy index của các property được chỉ định
    propList = getPropIndex(data, ','.join(args.prop))
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

def widthBin(data, args):
    # Lấy index của các property được chỉ định
    propList = getPropIndex(data, ','.join(args.prop))
    # Số lượng giỏ
    binCount = int(args.bin)
    # Chuyển vị data để thuận tiện xử lý
    pData = [[row[i] for row in data] for i in range(len(data[0]))]
    # Với mỗi property, tính độ rộng của giỏ, rồi chia các instance vào (thêm thuộc tính Bin)
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

def depthBin(data, args):
    # Lấy index của các property được chỉ định
    propList = getPropIndex(data, ','.join(args.prop))
    # Số lượng giỏ
    binCount = int(args.bin)
    if binCount > len(data) - 1:
        print('No.bins is larger than No.instances.')
        sys.exit()
    # Số phần tử trong mỗi giỏ
    eleCount = int((len(data) - 1) // binCount) + 1
    # Với mỗi property, sort lại danh sách theo property này, gọi binEdge[i] là phần tử cuối cùng của giỏ thứ i
    # Tìm các binEdge[i] sao cho eleCount - 1 <= binEdge[i] - binEdge[i - 1] <= eleCount
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
            propBinLower = data[binEdge[binIndex] + 1][prop]
            propBinUpper = data[min(binEdge[binIndex + 1] + 1, len(data) - 1)][prop]
            for inst in range(binEdge[binIndex], binEdge[binIndex + 1]):
                data[inst + 1] += ['[{},{}]'.format(propBinLower, propBinUpper)]
        data[0] += [data[0][prop] + 'DepthBin']
    return data

def remove(data, args):
    # Lấy index của các property được chỉ định
    propList = getPropIndex(data, ','.join(args.prop))
    # Với mỗi property, instance nào không bị trống property này (nghĩa là instance hợp lệ) thì được copy vào biến pData
    pData = list()
    for prop in propList:
        pData = [data[0]]
        for inst in range(len(data) - 1):
            if data[inst + 1][prop] not in ['', []]:
                pData += [data[inst + 1]]
        data = pData
    return pData

def fillIn(data, args):
    # Lấy index của các property được chỉ định
    propList = getPropIndex(data, ','.join(args.prop))
    # Với mỗi property, tính mean (đối với kiểu numeric) hoặc mode (đối với kiểu non-numeric) rồi điền vào chỗ còn khuyết
    pData = remove(data, args)
    pData = [[row[i] for row in pData] for i in range(len(pData[0]))]
    for prop in propList:
        try:
            # Thuộc tính numeric
            mean = sum(pData[prop][1:]) / (len(pData[prop]) - 1)
            for inst in range(len(data) - 1):
                if data[inst + 1][prop] in ['', []]:
                    data[inst + 1][prop] = mean
        except TypeError:
            # Thuộc tính non-numeric
            count = [[pData[prop][1:].count(value), value] for value in set(pData[prop][1:])]
            count.sort()
            for inst in range(len(data) - 1):
                if data[inst + 1][prop] in ['', []]:
                    data[inst + 1][prop] = count[-1][1]
    return data

def main():
    # Tham số dòng lệnh
    parser = argparse.ArgumentParser(description = 'Data preprocessing')
    parser.add_argument('--input', help = 'path to input file', required = True)
    parser.add_argument('--output', help = 'path to output file', required = True)
    parser.add_argument('--task', help = 'preprocessing task', required = True)
    parser.add_argument('--prop', help = 'property list', required = True, nargs = '*')
    parser.add_argument('--newMinMax', help = 'new min and max for min-max normalization', nargs = 2)
    parser.add_argument('--bin', help = 'number of bins for denormalization')
    args = parser.parse_args()

    data = list()
    # Mở file input
    try:
        fint = open(args.input, 'r', encoding = 'utf-8-sig')
    except Exception:
        print('No such files or directories.')
        sys.exit()
    # Đọc dữ liệu vào biến data, chuyển chuỗi sang số
    for row in csv.reader(fint):
        for prop in range(len(row)):
            try:
                row[prop] = eval(row[prop])
            except Exception:
                pass
        data += [row]
    fint.close()

    # Xử lý
    switcher = {'minMaxNorm': minMaxNorm, 'zScoreNorm': zScoreNorm, 'widthBin': widthBin, 'depthBin': depthBin, 'remove': remove, 'fillIn': fillIn}
    func = switcher.get(args.task, lambda a1, a2: [])
    try:
        data = func(data, args)
    except TypeError:
        print('Some properties are empty or not numerical')
        sys.exit()
    if data == []:
        print('Unknown task.')
        sys.exit()

    # Ghi data ra file output và đóng file
    fout = open(args.output, 'w', encoding = 'utf-8-sig', newline = '')
    csv.writer(fout).writerows(data)
    fout.close()

main()