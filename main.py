import yolov5
import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
model = yolov5.load(r"C:\\Users\\solomon\\Desktop\\AI_project_3\\yolov5_best.pt")

def main():
    img = 'model_test/test_1.png'
    result = model(img, size=500, augment=False)
    devices = get_devices(result)
    devices = label_devices(devices)
    # for i in devices:
        # print(f'{i['class_name']} at {(i['x1'], i['y1'])},  {(i['x2'], i['y2'])}')
    
    print('\n')
    
    topology = get_topology(devices)
    for key, value in topology.items():
        print(f'{value[0]}', ' ' * (5 - len(value[0])) ,f'<-----{key}---->     {value[1]}')

        
    lans = get_lans(topology.copy())
    print('lans     ', lans)
    print('topology:  ', topology)


    print("\n-------------GENERATING CHEETSHEET-----------------\n")    
    result.show()


def get_devices(model_dected_result):
    boxes = model_dected_result.xyxy[0]  
    class_names = {0:'R', 1:'SW', 2:'FW', 3:'WAN', 4:'Eth'}
    devices = []
    for i, box in enumerate(boxes):
        x1, y1, x2, y2, confidence, class_id = box.tolist()
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
        class_name = class_names[int(class_id)]
        entry = {'class_name': class_name,
                'x1':x1,
                'x2':x2,
                'y1':y1,
                'y2':y2,
                'confidence': confidence,
                'class_id': class_id}
        

        devices.append(entry)
    
    devices.sort(key=lambda device: device['x1']**2 + device['y1']**2)
    return devices

def label_devices(devices):
    tracker = {float(k):1 for k in range(5)}

    for i in devices:
        dev_id = i['class_id']
        dev_name = i['class_name']

        if dev_id in list(tracker.keys()):
            new_dev_name = dev_name + str(tracker[dev_id])
            tracker[dev_id] += 1
        else:
            tracker[dev_id] = 1
            new_dev_name = dev_name + '1'
        
        i['class_name'] = new_dev_name
    
    return devices

def find_conn(device, eth, dir):
    offset = 50
    if dir == 't':
        return ((device['x1'] - offset < eth['x1'] < device['x2'] + offset) and
            device['y1'] - offset <= eth['y2'] <= device['y1'] + offset)        

    elif dir == 'b':
        return ((device['x1'] - offset < eth['x1'] < device['x2'] + offset) and
            device['y2'] - offset <= eth['y1'] <= device['y2'] + offset)

    elif dir == 'r':
        return ((device['y1'] - offset < eth['y1'] < device['y2'] + offset) and
            device['x2'] - offset <= eth['x1'] <= device['x2'] + offset)

    elif dir == 'l':
        return ((device['y1'] - offset < eth['y2'] < device['y2'] + offset) and
            device['x1'] - offset <= eth['x2'] <= device['x1'] + offset)

def find_neighbour(devices, eth, dir):
    for i in devices:
        if i['class_id'] != 4.0:
            if dir == 't':
                if find_conn(i, eth, 'b'):
                    return i
            
            elif dir == 'b':
                if find_conn(i, eth, 't'):
                    return i
                
            elif dir == 'r':
                if find_conn(i, eth, 'l'):
                    return i
            
            elif dir == 'l':
                if find_conn(i, eth, 'r'):
                    return i

def get_topology(devices):
    Topology = {}
    types_of_con = ['t','b','r','l']
    
    for dev in devices:
        if dev['class_id'] != 4: 
            for eth in devices:
                if eth['class_id'] == 4:
                    for t_conn in types_of_con:
                        if find_conn(dev, eth, t_conn):
                            print(f'{eth['class_name']} {(eth['x1'], eth['y1'])},  {(eth['x2'], eth['y2'])} is connected to the ', dev['class_name'], 'from', t_conn)
                            neighbour = find_neighbour(devices, eth, t_conn)
                            if neighbour:
                                Topology[eth['class_name']] = [dev['class_name'], neighbour['class_name']]

    return Topology

def get_lans(obj):
    tem_obj = obj.copy()
    lans = {}
    for i in tem_obj:
        set_i = set(tem_obj[i]) # set_i = (SW1, SW2)   or set_i = (ETH1, ETH2)
        for j in tem_obj:
            if i != j:
                set_j = set(tem_obj[j])
                inter = set_i.intersection(set_j)
                inter = list(inter)[0] if inter else ""
                if inter[:2] == 'SW' or inter[:2] == 'ET':
                    temp = tem_obj[i] + tem_obj[j]
                    temp = set(temp)
                    temp = list(temp)
                    lans[f'lan_{len(lans)+1}'] = [i, j]
                    # update the obj dictionary
                    # print(temp)
                    # print('obj, ', obj)
                    # print('temp-obj', tem_obj)

                    try:
                        del obj[i]
                        del obj[j]
                    except:
                        pass

                    if sorted(temp) not in [sorted(i) for i in list(obj.values())]:
                        obj[f'lan_{len(obj) + 1}'] = temp


    for i in tem_obj.keys():
        exist = False
        for j in list(lans.values()):
            if i in j:
                exist = True
        if not exist:
            lans[f'lan_{len(lans)+1}'] = [i]
    
    initial_result = lan_dectector(lans)
    for i in range(10):
        optimised_result = lan_dectector(initial_result)
        if optimised_result == initial_result:
            return optimised_result

        initial_result = optimised_result
            
    return optimised_result

def lan_dectector(lans):
    lans = list(lans.values())
    lans = [sorted(lan) for lan in lans]
    non_dup = {}
    merged_pairs = []

    for i in lans:
        intersect_count = 0
        for j in lans:
            if i != j:
                i_set = set(i)
                j_set = set(j) 
                intersect = i_set.intersection(j_set)
                if intersect:
                    intersect_count += 1
                    if(i, j)  not in merged_pairs and (j, i) not in merged_pairs:
                        intersect_count += 1
                        merged_lan = i_set.union(j_set)
                        non_dup[f'lan_{len(non_dup) + 1}'] = sorted(list(merged_lan))
                        merged_pairs.append((i, j))
        
        if intersect_count == 0:
            non_dup[f'lan_{len(non_dup) + 1}'] = i
        
        
    new_lan = {}
    for lan in non_dup:
        if non_dup[lan] not in list(new_lan.values()):
            new_lan[f'lan_{len(new_lan)+1}'] = non_dup[lan] 
                
    
    return new_lan
        

main()



