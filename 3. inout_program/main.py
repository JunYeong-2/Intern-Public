from import_file import *


model = torch.hub.load('ultralytics/yolov5', 'yolov5x')
path = 'C:\\Users\\Lee\\Desktop\\cctv_images\\cctv_org\\b1\\'
name = '021.jpg'
img = path + name
results = model(img)
results.save()

df = results.pandas().xyxy[0]
df['x_jum'] = (df['xmin'] + df['xmax']) / 2
df['y_jum'] = df['ymin'] + (df['ymax'] - df['ymin']) * 0.9
df.iloc[:,-2:] = df.iloc[:,-2:].astype('int')


for (path, dir, files) in os.walk("C:\\Users\\Lee\Desktop\\ves_lee_copy\\runs\\"):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        if ext == '.jpg':
            yolo_path = ("%s\\%s" % (path, filename))


image = cv2.imread(yolo_path)

for i in range(len(df)):
    image = cv2.line(image, (df['x_jum'].iloc[i], df['y_jum'].iloc[i]), (df['x_jum'].iloc[i], df['y_jum'].iloc[i]), (255,0,0), thickness=10)
cv2.waitKey(0)
cv2.destroyAllWindows()


default = image.copy()

pt1, pt2 = (0, 0), (0, 0)
drawing = False
lines = []

# Create a callback function
def draw_line(event, x, y, flags, param):
    global pt1, pt2, drawing, lines
    if event == cv2.EVENT_LBUTTONDOWN:
        pt1 = (x, y)
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img = param[0]
            color = param[1]
            thickness = param[2]
            pt2 = (x, y)
            img = cv2.line(img, pt1, pt2, color, thickness)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        lines.append((pt1, pt2))
        print("Line saved: ", pt1, pt2)

# Create a blank image
img = image.copy()

# Set the callback function for the window
cv2.namedWindow("Line")
cv2.setMouseCallback("Line", draw_line, [img, (0,0,255), 5])

# Show the window
while True:
    cv2.imshow("Line", img)
    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite('image.jpg', img)
        print("Image saved")
    if key == ord('q'):
        break

# Saving the coordinates to CSV
df2 = pd.DataFrame(lines, columns=["Start Point","End Point"])
df2.to_csv("coordinates.csv", index=False)

# Close the window
cv2.destroyAllWindows()

###

df3 = pd.DataFrame(columns=['x', 'y'])
x_list = []
y_list = []

def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coordinates: (", x, ",", y, ")")
        x_list.append(x)
        y_list.append(y)

# Create a window and set the mouse callback function
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", get_coordinates)

# Show the image
cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

if len(x_list) == 0:
    pass
else:
    df3['x'] = x_list
    df3['y'] = y_list
    df3['dir'] = df3['x'] >= 960
    
    df['del'] = False
    for i in range(len(df3)):
        if df3['dir'][i]:
            df['del'] = (df['x_jum'] >= df3['x'][i]) & (df['y_jum'] <= df3['y'][i]) | df['del']            
        else:
            df['del'] = (df['x_jum'] <= df3['x'][i]) & (df['y_jum'] <= df3['y'][i]) | df['del']            
            
            
            
    idx = df[df['del']].index
    df.drop(idx, inplace=True)


###

line = pd.read_csv('coordinates.csv')
line['Start Point'].str[1:-1].str.split(', ')

x1 = []
for i in range(len(line)):
    x1.append(line['Start Point'].str[1:-1].str.split(', ')[i][0])
line['x1'] = x1
y1 = []
for i in range(len(line)):
    y1.append(line['Start Point'].str[1:-1].str.split(', ')[i][1])
line['y1'] = y1

x2 = []
for i in range(len(line)):
    x2.append(line['End Point'].str[1:-1].str.split(', ')[i][0])
line['x2'] = x2
y2 = []
for i in range(len(line)):
    y2.append(line['End Point'].str[1:-1].str.split(', ')[i][1])
line['y2'] = y2


draw = line.iloc[:,-4:].astype('int')

line.drop(columns=['Start Point', 'End Point'], inplace=True)
line = line.astype('int')

line['xmax'] = line.loc[:,['x1','x2']].max(axis=1)
line['xmin'] = line.loc[:,['x1','x2']].min(axis=1)

line['ymax'] = line.loc[:,['y1','y2']].max(axis=1)
line['ymin'] = line.loc[:,['y1','y2']].min(axis=1)

col = line.columns[:-4]
line.drop(columns=col, inplace=True)



left_right = (line['xmax'] + line['xmin']) / 2 < 960
left_right_list = []

for i in left_right:
    if i:
        left_right_list.append('left')
    else:
        left_right_list.append('right')
line['dir'] = left_right_list

line.loc[line['dir'] == 'left', 'xmin'] = 0
line.loc[line['dir'] == 'right', 'xmax'] = 1920

path = yolo_path

isdraw = False
result = ""
count = 1
cctv_num = ""
x1, y1 = 0, 0
BLUE = (255, 0, 0)

data = {}
# roi_data = []
roi_data = ""

x1_list = []
y1_list = []
x2_list = []
y2_list = []

# Define the event listener function for the mouse clicks
def clickcallback(event, x, y, flags, param):
    global isdraw
    global result
    global x1, y1
    global imgs
    global roi_data

    if event == cv2.EVENT_LBUTTONDOWN: # 좌표 기록 시작 및 ROI 박스 그리기 시작
        if isdraw:
            result = result + ", " + str(x) + ", " + str(y)
            roi_data = roi_data + f", {x}, {y}]"
            
            x2_list.append(x)
            y2_list.append(y)

            print(result)
            isdraw = False
            w = x - x1
            h = y - y1
            if w > 0 and h > 0:
                cv2.rectangle(imgs, (x1, y1), (x, y), BLUE, 1)
        else:
            result = result + ', ' + str(x) + ", " + str(y)
            
            x1_list.append(x)
            y1_list.append(y)
            
            roi_data = f"[{x}, {y}"
            isdraw = True
            x1 = x
            y1 = y
            
#     x1_list.append(x1)
#     y1_list.append(y1)
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if isdraw:
            img_draw = imgs.copy()
            cv2.rectangle(img_draw, (x1, y1), (x, y), BLUE, 1, cv2.LINE_AA)
            cv2.imshow('img', img_draw)
            
cv2.namedWindow('img')

for img in sorted(glob.glob(path)):
    imgs = cv2.imread(img)
    cv2.imshow("img", imgs)
    cv2.setMouseCallback("img", clickcallback)

    k = cv2.waitKey(0)

    if k == 27: # esc key
        isdraw = False
        cv2.destroyAllWindows()

front = pd.DataFrame({'xmin':x1_list,
              'xmax':x2_list,
              'ymin':y1_list,
              'ymax':y2_list})

line = pd.concat([line, front])
line = line.reset_index().drop(columns='index')

front.columns = ['x1', 'x2', 'y1', 'y2']
draw = pd.concat([draw, front])
draw = draw.reset_index().drop(columns='index')



null_list = []
for i in range(len(line)):
    for j in range(len(df)):
        if line.iloc[i]['xmin']<= df.iloc[j]['x_jum'] and df.iloc[j]['x_jum'] <= line.iloc[i]['xmax'] and line.iloc[i]['ymin']<=df.iloc[j]['y_jum'] and df.iloc[j]['y_jum']<=line.iloc[i]['ymax']:
            null_list.append(i)
        else:
            pass
        
a = set(null_list)
a = list(a)


draw['color'] = np.nan

draw.loc[a, 'color'] = 'yello'
draw['color'] = draw['color'].fillna('green')


for i in range(len(draw)):
    if draw.loc[i]['color'] == 'yello':
        img = cv2.line(default, (draw.iloc[i]['x1'], draw.iloc[i]['y1']), (draw.iloc[i]['x2'], draw.iloc[i]['y2']), (0,255, 255), 5)
    elif draw.loc[i]['color'] == 'green':
        img = cv2.line(default, (draw.iloc[i]['x1'], draw.iloc[i]['y1']), (draw.iloc[i]['x2'], draw.iloc[i]['y2']), (0,128,0), 5)

cv2.imshow('hello', img)
cv2.imwrite('finally.jpg',img)
cv2.waitKey()
cv2.destroyAllWindows()
